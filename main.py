import os
import sys
from datetime import datetime

# Adiciona o diretório raiz ao sys.path para permitir importações absolutas
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
sys.path.insert(0, project_root)

from db.conexao import inicializar_banco
from modelos import evento as modelo_evento
from modelos import convidado as modelo_convidado
from servicos import qrcode_service
from servicos import convite_service

# --- Funções Auxiliares de Interface ---

def limpar_tela():
    """Limpa o terminal."""
    os.system("cls" if os.name == "nt" else "clear")

def pausar(mensagem="Pressione Enter para continuar..."):
    """Pausa a execução e espera o usuário pressionar Enter."""
    input(mensagem)

def exibir_cabecalho(titulo):
    """Exibe um cabeçalho formatado."""
    limpar_tela()
    print("=" * 40)
    print(titulo.center(40))
    print("=" * 40)
    print()

def obter_input(prompt, tipo=str, obrigatorio=True, padrao=None):
    """Solicita input do usuário com validação de tipo e obrigatoriedade."""
    while True:
        valor_str = input(prompt).strip()
        if not valor_str:
            if obrigatorio and padrao is None:
                print("Erro: Este campo é obrigatório.")
                continue
            elif padrao is not None:
                return padrao
            else: # Não obrigatório e sem valor
                return None

        try:
            if tipo == int:
                return int(valor_str)
            elif tipo == float:
                return float(valor_str)
            elif tipo == "data": # Formato DD-MM-AAAA
                return datetime.strptime(valor_str, "%d-%m-%Y").date()
            elif tipo == "hora": # Formato HH:MM
                return datetime.strptime(valor_str, "%H:%M").time()
            elif tipo == "email":
                if "@" not in valor_str or "." not in valor_str.split("@")[-1]:
                    raise ValueError("Formato de e-mail inválido.")
                return valor_str
            elif tipo == "status_presenca":
                valor_lower = valor_str.lower()
                if valor_lower not in ["pendente", "presente", "ausente"]:
                    raise ValueError("Status inválido. Use 'pendente', 'presente' ou 'ausente'.")
                return valor_lower
            else:
                return valor_str # Retorna como string por padrão
        except ValueError as e:
            print(f"Erro: Entrada inválida ({e}). Por favor, tente novamente.")

# --- Funções de Gerenciamento de Eventos ---

def criar_novo_evento():
    exibir_cabecalho("Criar Novo Evento")
    nome = obter_input("Nome do Evento: ")
    local = obter_input("Local: ", obrigatorio=False)
    data = obter_input("Data (DD-MM-YYYY): ", tipo="data", obrigatorio=False)
    horario = obter_input("Horário (HH:MM): ", tipo="hora", obrigatorio=False)
    descricao = obter_input("Descrição: ", obrigatorio=False)

    evento_id = modelo_evento.criar_evento(nome, local, data, horario, descricao)
    if evento_id:
        print(f"\nEvento '{nome}' criado com sucesso (ID: {evento_id}).")
    else:
        print("\nFalha ao criar o evento.")
    pausar()

def listar_todos_eventos(selecionar=False):
    exibir_cabecalho("Listar Eventos")
    eventos = modelo_evento.listar_eventos()
    if not eventos:
        print("Nenhum evento cadastrado.")
        pausar()
        return None if selecionar else False

    print("{:<5} {:<30} {:<15} {:<10} {:<10}".format("ID", "Nome", "Local", "Data", "Hora"))
    print("-"*75)
    for ev in eventos:
        print("{:<5} {:<30} {:<15} {:<10} {:<10}".format(
            ev["id"],
            ev["nome"][:28] + ".." if len(ev["nome"]) > 30 else ev["nome"],
            (ev["local"] or "N/D")[:13] + ".." if ev["local"] and len(ev["local"]) > 15 else (ev["local"] or "N/D"),
            ev["data"] or "N/D",
            ev["horario"] or "N/D"
        ))
    print("-"*75)

    if selecionar:
        while True:
            try:
                evento_id_str = obter_input("\nDigite o ID do evento desejado (ou 0 para cancelar): ", tipo=str)
                if evento_id_str == '0':
                    return None # Cancelado pelo usuário
                evento_id = int(evento_id_str)
                # Verifica se o ID existe na lista buscada
                if any(ev["id"] == evento_id for ev in eventos):
                    return evento_id
                else:
                    print("Erro: ID do evento inválido.")
            except ValueError:
                print("Erro: ID deve ser um número.")
    else:
        pausar()
        return True

def editar_evento_existente():
    exibir_cabecalho("Editar Evento")
    evento_id = listar_todos_eventos(selecionar=True)
    if not evento_id:
        print("\nOperação cancelada ou nenhum evento para editar.")
        pausar()
        return # Nenhum evento para editar ou usuário cancelou

    evento_atual = modelo_evento.buscar_evento_por_id(evento_id)
    if not evento_atual:
        print(f"Erro: Evento com ID {evento_id} não encontrado.")
        pausar()
        return

    print(f"\nEditando Evento: {evento_atual['nome']}")
    print("Deixe em branco para manter o valor atual.")

    nome = obter_input(f"Novo Nome [{evento_atual['nome']}]: ", obrigatorio=False, padrao=evento_atual["nome"])
    local = obter_input(f"Novo Local [{evento_atual['local'] or 'N/D'}]: ", obrigatorio=False, padrao=evento_atual["local"])
    data = obter_input(f"Nova Data (YYYY-MM-DD) [{evento_atual['data'] or 'N/D'}]: ", tipo="data", obrigatorio=False, padrao=evento_atual["data"])
    horario = obter_input(f"Novo Horário (HH:MM) [{evento_atual['horario'] or 'N/D'}]: ", tipo="hora", obrigatorio=False, padrao=evento_atual["horario"])
    descricao = obter_input(f"Nova Descrição [{evento_atual['descricao'] or 'N/D'}]: ", obrigatorio=False, padrao=evento_atual["descricao"])

    if modelo_evento.atualizar_evento(evento_id, nome, local, data, horario, descricao):
        print("\nEvento atualizado com sucesso!")
    else:
        print("\nFalha ao atualizar o evento.")
    pausar()

def excluir_evento_existente():
    exibir_cabecalho("Excluir Evento")
    evento_id = listar_todos_eventos(selecionar=True)
    if not evento_id:
        print("\nOperação cancelada ou nenhum evento para excluir.")
        pausar()
        return

    evento = modelo_evento.buscar_evento_por_id(evento_id)
    if not evento:
        print(f"Erro: Evento com ID {evento_id} não encontrado.")
        pausar()
        return

    confirmacao = input(f"Tem certeza que deseja excluir o evento '{evento['nome']}' (ID: {evento_id}) e TODOS os seus convidados? (s/N): ").lower()

    if confirmacao == "s":
        if modelo_evento.deletar_evento(evento_id):
            print("\nEvento excluído com sucesso!")
        else:
            print("\nFalha ao excluir o evento.")
    else:
        print("\nExclusão cancelada.")
    pausar()

# --- Funções de Gerenciamento de Convidados ---

def criar_novo_convidado():
    exibir_cabecalho("Criar Novo Convidado e Gerar Convite")

    print("Selecione o evento para adicionar o convidado:")
    evento_id = listar_todos_eventos(selecionar=True)
    if not evento_id:
        print("\nNenhum evento selecionado. Criação de convidado cancelada.")
        pausar()
        return

    evento = modelo_evento.buscar_evento_por_id(evento_id)
    if not evento:
        print(f"Erro: Evento com ID {evento_id} não encontrado.")
        pausar()
        return

    print(f"\nAdicionando convidado ao evento: {evento['nome']}")
    nome = obter_input("Nome do Convidado: ")
    email = obter_input("E-mail: ", tipo="email", obrigatorio=False)
    telefone = obter_input("Telefone: ", obrigatorio=False)
    status = obter_input("Status Presença (pendente/presente/ausente) [pendente]: ", tipo="status_presenca", obrigatorio=False, padrao="pendente")

    convidado_id = modelo_convidado.criar_convidado(evento_id, nome, email, telefone, status)

    if convidado_id:
        print(f"\nConvidado '{nome}' (ID: {convidado_id}) criado com sucesso.")

        # Gerar QR Code e Convite PDF
        gerar_convite = input("Deseja gerar o convite em PDF com QR Code agora? (s/N): ").lower()
        if gerar_convite == "s":
            convidado = modelo_convidado.buscar_convidado_por_id(convidado_id)
            if not convidado:
                print("Erro ao buscar dados do convidado recém-criado.")
                pausar()
                return

            # Opção para tipo de QR Code
            tipo_qr = input("Tipo de QR Code (dados/url) [dados]: ").lower() or "dados"
            if tipo_qr == "url":
                conteudo_qr = obter_input("Digite a URL para o QR Code: ")
            else:
                # Dados padrão para o QR Code
                conteudo_qr = f"Evento: {evento['nome']}\nConvidado: {convidado['nome']}\nID Convidado: {convidado_id}"
                conteudo_qr_formatado = conteudo_qr.replace('\n', ' | ')
                print(f"Usando dados padrão para o QR Code: {conteudo_qr_formatado}")

            nome_arquivo_base = f"evento_{evento_id}_convidado_{convidado_id}_{nome.replace(' ', '_').lower()}"

            print("\nGerando QR Code...")
            caminho_qrcode = qrcode_service.gerar_qrcode(conteudo_qr, nome_arquivo_base, tipo=tipo_qr)

            if caminho_qrcode:
                print("Gerando Convite PDF...")
                # Passar o dicionário completo do evento e convidado
                # Precisamos buscar o evento novamente para garantir que temos data/hora como objetos
                evento_para_pdf = modelo_evento.buscar_evento_por_id(evento_id)
                if not evento_para_pdf:
                     print("Erro crítico: Não foi possível re-buscar dados do evento para o PDF.")
                     pausar()
                     return

                caminho_pdf = convite_service.gerar_convite_pdf(evento_para_pdf, convidado, caminho_qrcode, nome_arquivo_base)
                if caminho_pdf:
                    print(f"\nConvite gerado com sucesso: {caminho_pdf}")
                else:
                    print("\nFalha ao gerar o convite PDF.")
            else:
                print("\nFalha ao gerar o QR Code. O convite PDF não pode ser gerado.")
    else:
        print("\nFalha ao criar o convidado.")
    pausar()

def listar_convidados_de_evento():
    exibir_cabecalho("Listar Convidados por Evento")
    print("Selecione o evento para listar os convidados:")
    evento_id = listar_todos_eventos(selecionar=True)
    if not evento_id:
        print("\nOperação cancelada ou nenhum evento selecionado.")
        pausar()
        return

    evento = modelo_evento.buscar_evento_por_id(evento_id)
    if not evento:
        print(f"Erro: Evento com ID {evento_id} não encontrado.")
        pausar()
        return

    exibir_cabecalho(f"Convidados do Evento: {evento['nome']}")
    convidados = modelo_convidado.listar_convidados_por_evento(evento_id)

    if not convidados:
        print("Nenhum convidado cadastrado para este evento.")
    else:
        print("{:<5} {:<30} {:<30} {:<15} {:<10}".format("ID", "Nome", "E-mail", "Telefone", "Status"))
        print("-"*95)
        for conv in convidados:
            print("{:<5} {:<30} {:<30} {:<15} {:<10}".format(
                conv["id"],
                conv["nome"][:28] + ".." if len(conv["nome"]) > 30 else conv["nome"],
                (conv["email"] or "N/D")[:28] + ".." if conv["email"] and len(conv["email"]) > 30 else (conv["email"] or "N/D"),
                conv["telefone"] or "N/D",
                conv["status_presenca"]
            ))
        print("-"*95)
    pausar()

def listar_todos_os_convidados(selecionar=False):
    """Lista todos os convidados de todos os eventos."""
    exibir_cabecalho("Listar Todos os Convidados")
    convidados = modelo_convidado.listar_todos_convidados()
    if not convidados:
        print("Nenhum convidado cadastrado no sistema.")
        pausar()
        return None if selecionar else False

    print("{:<5} {:<25} {:<25} {:<15} {:<10} {:<20}".format("ID", "Nome", "E-mail", "Telefone", "Status", "Evento"))
    print("-"*110)
    for conv in convidados:
        nome_evento = conv["nome_evento"][:18] + ".." if len(conv["nome_evento"]) > 20 else conv["nome_evento"]
        print("{:<5} {:<25} {:<25} {:<15} {:<10} {:<20}".format(
            conv["id"],
            conv["nome"][:23] + ".." if len(conv["nome"]) > 25 else conv["nome"],
            (conv["email"] or "N/D")[:23] + ".." if conv["email"] and len(conv["email"]) > 25 else (conv["email"] or "N/D"),
            conv["telefone"] or "N/D",
            conv["status_presenca"],
            f" {nome_evento} (ID:{conv['evento_id']})"
        ))
    print("-"*110)

    if selecionar:
        while True:
            try:
                convidado_id_str = obter_input("\nDigite o ID do convidado desejado (ou 0 para cancelar): ", tipo=str)
                if convidado_id_str == '0':
                    return None # Cancelado pelo usuário
                convidado_id = int(convidado_id_str)
                # Verifica se o ID existe na lista buscada
                if any(c["id"] == convidado_id for c in convidados):
                    return convidado_id
                else:
                    print("Erro: ID do convidado inválido.")
            except ValueError:
                print("Erro: ID deve ser um número.")
    else:
        pausar()
        return True

def editar_convidado_existente():
    exibir_cabecalho("Editar Convidado")
    convidado_id = listar_todos_os_convidados(selecionar=True)
    if not convidado_id:
        print("\nOperação cancelada ou nenhum convidado para editar.")
        pausar()
        return

    convidado_atual = modelo_convidado.buscar_convidado_por_id(convidado_id)
    if not convidado_atual:
        print(f"Erro: Convidado com ID {convidado_id} não encontrado.")
        pausar()
        return

    print(f"\nEditando Convidado: {convidado_atual['nome']} (Evento: {convidado_atual['nome_evento']})")
    print("Deixe em branco para manter o valor atual.")

    nome = obter_input(f"Novo Nome [{convidado_atual['nome']}]: ", obrigatorio=False, padrao=convidado_atual["nome"])
    email = obter_input(f"Novo E-mail [{convidado_atual['email'] or 'N/D'}]: ", tipo="email", obrigatorio=False, padrao=convidado_atual["email"])
    telefone = obter_input(f"Novo Telefone [{convidado_atual['telefone'] or 'N/D'}]: ", obrigatorio=False, padrao=convidado_atual["telefone"])
    status = obter_input(f"Novo Status [{convidado_atual['status_presenca']}] (pendente/presente/ausente): ", tipo="status_presenca", obrigatorio=False, padrao=convidado_atual["status_presenca"])

    if modelo_convidado.atualizar_convidado(convidado_id, nome, email, telefone, status):
        print("\nConvidado atualizado com sucesso!")
    else:
        print("\nFalha ao atualizar o convidado. Verifique se o e-mail já existe.")
    pausar()

def excluir_convidado_existente():
    exibir_cabecalho("Excluir Convidado")
    convidado_id = listar_todos_os_convidados(selecionar=True)
    if not convidado_id:
        print("\nOperação cancelada ou nenhum convidado para excluir.")
        pausar()
        return

    convidado = modelo_convidado.buscar_convidado_por_id(convidado_id)
    if not convidado:
        print(f"Erro: Convidado com ID {convidado_id} não encontrado.")
        pausar()
        return

    confirmacao = input(f"Tem certeza que deseja excluir o convidado '{convidado['nome']}' (ID: {convidado_id}) do evento '{convidado['nome_evento']}'? (s/N): ").lower()

    if confirmacao == "s":
        if modelo_convidado.deletar_convidado(convidado_id):
            print("\nConvidado excluído com sucesso!")
        else:
            print("\nFalha ao excluir o convidado.")
    else:
        print("\nExclusão cancelada.")
    pausar()

# --- Menus da Interface ---

def menu_eventos():
    while True:
        exibir_cabecalho("Gerenciar Eventos")
        print("1. Criar Novo Evento")
        print("2. Listar Todos os Eventos")
        print("3. Editar Evento Existente")
        print("4. Excluir Evento Existente")
        print("0. Voltar ao Menu Principal")
        print()
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            criar_novo_evento()
        elif opcao == "2":
            listar_todos_eventos()
        elif opcao == "3":
            editar_evento_existente()
        elif opcao == "4":
            excluir_evento_existente()
        elif opcao == "0":
            break
        else:
            print("Opção inválida. Tente novamente.")
            pausar()

def menu_convidados():
    while True:
        exibir_cabecalho("Gerenciar Convidados e Convites")
        print("1. Adicionar Novo Convidado e Gerar Convite")
        print("2. Listar Convidados de um Evento")
        print("3. Listar Todos os Convidados")
        print("4. Editar Convidado Existente")
        print("5. Excluir Convidado Existente")
        print("0. Voltar ao Menu Principal")
        print()
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            criar_novo_convidado()
        elif opcao == "2":
            listar_convidados_de_evento()
        elif opcao == "3":
            listar_todos_os_convidados()
        elif opcao == "4":
            editar_convidado_existente()
        elif opcao == "5":
            excluir_convidado_existente()
        elif opcao == "0":
            break
        else:
            print("Opção inválida. Tente novamente.")
            pausar()

def menu_principal():
    while True:
        exibir_cabecalho("Sistema de Convites com QR Code")
        print("1. Gerenciar Eventos")
        print("2. Gerenciar Convidados e Convites")
        print("0. Sair")
        print()
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            menu_eventos()
        elif opcao == "2":
            menu_convidados()
        elif opcao == "0":
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida. Tente novamente.")
            pausar()

# --- Ponto de Entrada Principal ---

if __name__ == "__main__":
    print("Inicializando o sistema...")
    # Garante que o banco e as tabelas existam antes de iniciar
    # É necessário configurar as credenciais do MySQL via variáveis de ambiente
    # Ex: export DB_USER='seu_usuario' DB_PASSWORD='sua_senha' DB_HOST='seu_host' DB_NAME='convites_db'
    # Se não configuradas, usará padrões (localhost, root, sem senha, convites_db)
    print("Verificando/Inicializando banco de dados...")
    inicializar_banco()
    print("Banco de dados pronto.")
    pausar("Pressione Enter para iniciar a aplicação...")
    menu_principal()

# Fim do arquivo main.py
