# -*- coding: utf-8 -*-
from db.conexao import criar_conexao, fechar_conexao
import sqlite3 # Importar sqlite3 para tratar erros específicos

def criar_convidado(evento_id, nome, email, telefone, status_presenca="pendente"):
    """Cria um novo convidado associado a um evento no SQLite."""
    conexao = criar_conexao()
    if not conexao:
        return None
    cursor = conexao.cursor()
    try:
        # Verificar se o evento_id existe
        cursor.execute("SELECT id FROM eventos WHERE id = ?", (evento_id,))
        if cursor.fetchone() is None:
            print(f"Erro: Evento com ID {evento_id} não encontrado.")
            return None

        # Validar status_presenca antes de inserir
        if status_presenca not in ["pendente", "presente", "ausente"]:
             print(f"Erro: Status de presença 	\" {status_presenca}	\" inválido ao criar convidado.")
             return None

        sql = "INSERT INTO convidados (evento_id, nome, email, telefone, status_presenca) VALUES (?, ?, ?, ?, ?)"
        valores = (evento_id, nome, email, telefone, status_presenca)
        cursor.execute(sql, valores)
        conexao.commit()
        convidado_id = cursor.lastrowid
        print(f"Convidado 	\" {nome}	\" (ID: {convidado_id}) criado para o evento ID {evento_id}.")
        return convidado_id
    except sqlite3.IntegrityError as e:
        # Trata erro de chave única (email) ou chave estrangeira
        print(f"Erro de integridade ao criar convidado no SQLite: {e}")
        if "UNIQUE constraint failed: convidados.email" in str(e):
             print(f"Erro: O email 	\" {email}	\" já está cadastrado.")
        conexao.rollback()
        return None
    except sqlite3.Error as e:
        print(f"Erro ao criar convidado no SQLite: {e}")
        conexao.rollback()
        return None
    finally:
        cursor.close()
        fechar_conexao(conexao)

def listar_convidados_por_evento(evento_id):
    """Lista todos os convidados de um evento específico no SQLite."""
    conexao = criar_conexao()
    if not conexao:
        return []
    cursor = conexao.cursor()
    convidados = []
    try:
        sql = """SELECT c.id, c.nome, c.email, c.telefone, c.status_presenca, e.nome as nome_evento
                 FROM convidados c
                 JOIN eventos e ON c.evento_id = e.id
                 WHERE c.evento_id = ?
                 ORDER BY c.nome"""
        cursor.execute(sql, (evento_id,))
        convidados_raw = cursor.fetchall()
        convidados = [dict(row) for row in convidados_raw] # Converte para dict
    except sqlite3.Error as e:
        print(f"Erro ao listar convidados do evento ID {evento_id} no SQLite: {e}")
    finally:
        cursor.close()
        fechar_conexao(conexao)
    return convidados

def listar_todos_convidados():
    """Lista todos os convidados de todos os eventos no SQLite."""
    conexao = criar_conexao()
    if not conexao:
        return []
    cursor = conexao.cursor()
    convidados = []
    try:
        sql = """SELECT c.id, c.nome, c.email, c.telefone, c.status_presenca, e.nome as nome_evento, e.id as evento_id
                 FROM convidados c
                 JOIN eventos e ON c.evento_id = e.id
                 ORDER BY e.nome, c.nome"""
        cursor.execute(sql)
        convidados_raw = cursor.fetchall()
        convidados = [dict(row) for row in convidados_raw] # Converte para dict
    except sqlite3.Error as e:
        print(f"Erro ao listar todos os convidados no SQLite: {e}")
    finally:
        cursor.close()
        fechar_conexao(conexao)
    return convidados

def buscar_convidado_por_id(convidado_id):
    """Busca um convidado específico pelo seu ID no SQLite."""
    conexao = criar_conexao()
    if not conexao:
        return None
    cursor = conexao.cursor()
    convidado = None
    try:
        sql = """SELECT c.id, c.evento_id, c.nome, c.email, c.telefone, c.status_presenca, e.nome as nome_evento
                 FROM convidados c
                 JOIN eventos e ON c.evento_id = e.id
                 WHERE c.id = ?"""
        cursor.execute(sql, (convidado_id,))
        convidado_raw = cursor.fetchone()
        if convidado_raw:
            convidado = dict(convidado_raw) # Converte para dict
    except sqlite3.Error as e:
        print(f"Erro ao buscar convidado ID {convidado_id} no SQLite: {e}")
    finally:
        cursor.close()
        fechar_conexao(conexao)
    return convidado

def atualizar_convidado(convidado_id, nome, email, telefone, status_presenca):
    """Atualiza os dados de um convidado existente no SQLite."""
    conexao = criar_conexao()
    if not conexao:
        return False
    cursor = conexao.cursor()
    try:
        # Validar status_presenca
        if status_presenca not in ["pendente", "presente", "ausente"]:
            print(f"Erro: Status de presença 	\" {status_presenca}	\" inválido.")
            return False

        sql = """UPDATE convidados SET
                    nome = ?,
                    email = ?,
                    telefone = ?,
                    status_presenca = ?
                 WHERE id = ?"""
        valores = (nome, email, telefone, status_presenca, convidado_id)
        cursor.execute(sql, valores)
        conexao.commit()
        if cursor.rowcount == 0:
            print(f"Nenhum convidado encontrado com ID {convidado_id} para atualizar.")
            return False
        print(f"Convidado ID {convidado_id} atualizado com sucesso.")
        return True
    except sqlite3.IntegrityError as e:
        print(f"Erro de integridade ao atualizar convidado ID {convidado_id} no SQLite: {e}")
        if "UNIQUE constraint failed: convidados.email" in str(e):
             print(f"Erro: O email 	\" {email}	\" já está cadastrado para outro convidado.")
        conexao.rollback()
        return False
    except sqlite3.Error as e:
        print(f"Erro ao atualizar convidado ID {convidado_id} no SQLite: {e}")
        conexao.rollback()
        return False
    finally:
        cursor.close()
        fechar_conexao(conexao)

def deletar_convidado(convidado_id):
    """Deleta um convidado do banco de dados SQLite."""
    conexao = criar_conexao()
    if not conexao:
        return False
    cursor = conexao.cursor()
    try:
        # Verificar se o convidado existe
        cursor.execute("SELECT id FROM convidados WHERE id = ?", (convidado_id,))
        if cursor.fetchone() is None:
            print(f"Nenhum convidado encontrado com ID {convidado_id} para deletar.")
            return False

        cursor.execute("DELETE FROM convidados WHERE id = ?", (convidado_id,))
        conexao.commit()
        print(f"Convidado ID {convidado_id} deletado com sucesso.")
        return True
    except sqlite3.Error as e:
        print(f"Erro ao deletar convidado ID {convidado_id} no SQLite: {e}")
        conexao.rollback()
        return False
    finally:
        cursor.close()
        fechar_conexao(conexao)

# Exemplo de uso adaptado para SQLite
if __name__ == "__main__":
    from db.conexao import inicializar_banco
    # Import relativo funciona se executado de dentro do diretório raiz ou com PYTHONPATH ajustado
    try:
        from modelos.evento import criar_evento as criar_evento_teste, listar_eventos as listar_eventos_teste, deletar_evento as deletar_evento_teste
    except ImportError:
        # Fallback para import absoluto se o relativo falhar (ex: execução direta do script)
        import sys
        import os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from modelos.evento import criar_evento as criar_evento_teste, listar_eventos as listar_eventos_teste, deletar_evento as deletar_evento_teste
    from datetime import date, time

    print("Inicializando banco SQLite para testes do modelo Convidado...")
    inicializar_banco()

    print("\n--- Testando CRUD de Convidados (SQLite) ---")

    # Criar um evento para teste (se não existir)
    print("\n0. Verificando/Criando evento de teste...")
    eventos_existentes = listar_eventos_teste()
    evento_teste_id = None
    evento_criado_neste_teste = False
    if eventos_existentes:
        evento_teste_id = eventos_existentes[0]["id"]
        print(f"Usando evento existente ID: {evento_teste_id}")
    else:
        evento_teste_id = criar_evento_teste("Evento Teste Convidados SQLite", "Local Teste", date(2025, 12, 31), time(20, 0), "Evento para testar convidados.")
        if not evento_teste_id:
            print("Falha ao criar evento de teste. Abortando testes de convidado.")
            exit()
        evento_criado_neste_teste = True
        print(f"Evento de teste criado com ID: {evento_teste_id}")

    # Criar Convidados
    print("\n1. Criando convidados...")
    c1_id = criar_convidado(evento_teste_id, "Alice Silva SQLite", "alice.silva.sqlite@email.com", "(11) 98765-4321")
    c2_id = criar_convidado(evento_teste_id, "Bob Souza SQLite", "bob.souza.sqlite@email.com", "(21) 91234-5678", "presente")
    c3_id = criar_convidado(evento_teste_id, "Charlie Brown SQLite", "charlie.sqlite@email.com", None)
    # Teste de email duplicado
    criar_convidado(evento_teste_id, "Alice Duplicada", "alice.silva.sqlite@email.com", "(11) 00000-0000")
    # Teste de evento inexistente
    criar_convidado(9999, "Convidado Fantasma", "fantasma@email.com", None)

    # Listar Convidados por Evento
    print(f"\n2. Listando convidados do evento ID {evento_teste_id}...")
    convidados_evento = listar_convidados_por_evento(evento_teste_id)
    if convidados_evento:
        for conv in convidados_evento:
            print(f" - ID: {conv['id']}, Nome: {conv['nome']}, Email: {conv['email']}, Status: {conv['status_presenca']}")
    else:
        print("Nenhum convidado encontrado para este evento.")

    # Listar Todos os Convidados
    print("\n3. Listando todos os convidados...")
    todos_convidados = listar_todos_convidados()
    if todos_convidados:
        for conv in todos_convidados:
            print(f" - ID: {conv['id']}, Nome: {conv['nome']}, Evento: {conv['nome_evento']}({conv['evento_id']})")
    else:
        print("Nenhum convidado encontrado no sistema.")

    # Buscar por ID
    print("\n4. Buscando convidado por ID...")
    if c1_id:
        convidado_buscado = buscar_convidado_por_id(c1_id)
        if convidado_buscado:
            print(f"Convidado encontrado: {convidado_buscado['nome']}")
        else:
            print(f"Convidado ID {c1_id} não encontrado.")

    # Atualizar
    print("\n5. Atualizando convidado...")
    if c2_id:
        atualizado = atualizar_convidado(c2_id, "Roberto 	\"Bob	\" Souza SQLite", "bob.souza.sqlite@newemail.com", "(21) 99999-8888", "ausente")
        if atualizado:
            convidado_verificado = buscar_convidado_por_id(c2_id)
            print(f"Convidado atualizado: {convidado_verificado}")
        # Teste de status inválido
        atualizar_convidado(c2_id, "Roberto 	\"Bob	\" Souza SQLite", "bob.souza.sqlite@newemail.com", "(21) 99999-8888", "talvez")

    # Deletar
    print("\n6. Deletando convidado...")
    if c3_id:
        deletado = deletar_convidado(c3_id)
        if deletado:
            print(f"Convidado ID {c3_id} deletado.")
            convidado_deletado = buscar_convidado_por_id(c3_id)
            if not convidado_deletado:
                print("Confirmação: Convidado não encontrado após deleção.")

    # Limpeza (opcional): deletar o evento de teste criado
    if evento_criado_neste_teste:
        print("\n7. Limpando evento de teste...")
        deletar_evento_teste(evento_teste_id)
        print(f"Evento de teste ID {evento_teste_id} deletado.")

    print("\n--- Testes do modelo Convidado (SQLite) concluídos ---")

