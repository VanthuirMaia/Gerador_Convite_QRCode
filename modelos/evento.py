# -*- coding: utf-8 -*-
from db.conexao import criar_conexao, fechar_conexao
import sqlite3 # Importar sqlite3 para tratar erros específicos
from datetime import date, time, datetime # Para formatação

def criar_evento(nome, local, data, horario, descricao):
    """Cria um novo evento no banco de dados SQLite."""
    conexao = criar_conexao()
    if not conexao:
        return None
    cursor = conexao.cursor()
    try:
        # Formatar data e hora para TEXT (ISO format)
        data_str = data.isoformat() if isinstance(data, date) else data
        horario_str = horario.strftime("%H:%M") if isinstance(horario, time) else horario

        sql = "INSERT INTO eventos (nome, local, data, horario, descricao) VALUES (?, ?, ?, ?, ?)"
        valores = (nome, local, data_str, horario_str, descricao)
        cursor.execute(sql, valores)
        conexao.commit()
        evento_id = cursor.lastrowid
        print(f"Evento 	'{nome}' criado com sucesso. ID: {evento_id}")
        return evento_id
    except sqlite3.Error as e:
        print(f"Erro ao criar evento no SQLite: {e}")
        conexao.rollback()
        return None
    finally:
        cursor.close()
        fechar_conexao(conexao)

def listar_eventos():
    """Lista todos os eventos do banco de dados SQLite."""
    conexao = criar_conexao()
    if not conexao:
        return []
    # row_factory já está configurado em criar_conexao para retornar dict-like rows
    cursor = conexao.cursor()
    eventos = []
    try:
        # Ajuste na formatação de data/hora se necessário ao ler, mas SQLite guarda como TEXT
        cursor.execute("SELECT id, nome, local, data, horario, descricao FROM eventos ORDER BY data DESC, horario DESC")
        # Converter para dicionários explicitamente se row_factory não funcionar como esperado
        # ou processar os dados aqui
        eventos_raw = cursor.fetchall()
        eventos = [dict(row) for row in eventos_raw] # Converte sqlite3.Row para dict

        # Tentar formatar data/hora na leitura para exibição consistente
        for ev in eventos:
            try:
                if ev["data"]:
                    ev["data"] = datetime.strptime(ev["data"], "%Y-%m-%d").strftime("%d/%m/%Y")
            except (ValueError, TypeError):
                ev["data"] = ev["data"] or "N/D" # Mantém como está se falhar
            try:
                if ev["horario"]:
                     # Não precisa converter para strftime aqui, já é HH:MM
                     pass # Mantém HH:MM
            except (ValueError, TypeError):
                 ev["horario"] = ev["horario"] or "N/D"

    except sqlite3.Error as e:
        print(f"Erro ao listar eventos no SQLite: {e}")
    finally:
        cursor.close()
        fechar_conexao(conexao)
    return eventos

def buscar_evento_por_id(evento_id):
    """Busca um evento específico pelo seu ID no SQLite."""
    conexao = criar_conexao()
    if not conexao:
        return None
    cursor = conexao.cursor()
    evento = None
    try:
        cursor.execute("SELECT id, nome, local, data, horario, descricao FROM eventos WHERE id = ?", (evento_id,))
        evento_raw = cursor.fetchone()
        if evento_raw:
            evento = dict(evento_raw) # Converte para dict
            # Tentar converter data/hora para objetos datetime na busca
            try:
                if evento["data"]:
                    evento["data"] = datetime.strptime(evento["data"], "%Y-%m-%d").date()
            except (ValueError, TypeError):
                pass # Deixa como string se falhar
            try:
                if evento["horario"]:
                    evento["horario"] = datetime.strptime(evento["horario"], "%H:%M").time()
            except (ValueError, TypeError):
                pass # Deixa como string se falhar

    except sqlite3.Error as e:
        print(f"Erro ao buscar evento ID {evento_id} no SQLite: {e}")
    finally:
        cursor.close()
        fechar_conexao(conexao)
    return evento

def atualizar_evento(evento_id, nome, local, data, horario, descricao):
    """Atualiza os dados de um evento existente no SQLite."""
    conexao = criar_conexao()
    if not conexao:
        return False
    cursor = conexao.cursor()
    try:
        # Formatar data e hora para TEXT (ISO format)
        data_str = data.isoformat() if isinstance(data, date) else data
        horario_str = horario.strftime("%H:%M") if isinstance(horario, time) else horario

        sql = """UPDATE eventos SET
                    nome = ?,
                    local = ?,
                    data = ?,
                    horario = ?,
                    descricao = ?
                 WHERE id = ?"""
        valores = (nome, local, data_str, horario_str, descricao, evento_id)
        cursor.execute(sql, valores)
        conexao.commit()
        if cursor.rowcount == 0:
            print(f"Nenhum evento encontrado com ID {evento_id} para atualizar.")
            return False
        print(f"Evento ID {evento_id} atualizado com sucesso.")
        return True
    except sqlite3.Error as e:
        print(f"Erro ao atualizar evento ID {evento_id} no SQLite: {e}")
        conexao.rollback()
        return False
    finally:
        cursor.close()
        fechar_conexao(conexao)

def deletar_evento(evento_id):
    """Deleta um evento do banco de dados SQLite."""
    conexao = criar_conexao()
    if not conexao:
        return False
    cursor = conexao.cursor()
    try:
        # Verificar se o evento existe
        cursor.execute("SELECT id FROM eventos WHERE id = ?", (evento_id,))
        if cursor.fetchone() is None:
            print(f"Nenhum evento encontrado com ID {evento_id} para deletar.")
            return False

        # Deletar o evento (PRAGMA foreign_keys = ON cuidará dos convidados)
        cursor.execute("DELETE FROM eventos WHERE id = ?", (evento_id,))
        conexao.commit()
        print(f"Evento ID {evento_id} e seus convidados associados foram deletados com sucesso.")
        return True
    except sqlite3.Error as e:
        print(f"Erro ao deletar evento ID {evento_id} no SQLite: {e}")
        conexao.rollback()
        return False
    finally:
        cursor.close()
        fechar_conexao(conexao)

# Exemplo de uso adaptado para SQLite (pode ser removido ou comentado depois)
if __name__ == "__main__":
    from db.conexao import inicializar_banco
    print("Inicializando banco SQLite para testes do modelo Evento...")
    inicializar_banco()

    print("\n--- Testando CRUD de Eventos (SQLite) ---")

    # Criar
    print("\n1. Criando eventos...")
    ev1_id = criar_evento("Festa Junina Tech SQLite", "Escritório Central", date(2025, 6, 28), time(18, 0), "Arraiá da firma com SQLite!")
    ev2_id = criar_evento("Workshop Python SQLite", "Online via Zoom", date(2025, 7, 15), time(9, 0), "Aprofundamento em SQLite com Python.")
    ev3_id = criar_evento("Lançamento Produto Y SQLite", "Auditório Principal", date(2025, 8, 1), time(14, 30), None)

    # Listar
    print("\n2. Listando eventos...")
    eventos = listar_eventos()
    if eventos:
        for ev in eventos:
            # A formatação de data/hora agora é feita dentro de listar_eventos
            print(f" - ID: {ev['id']}, Nome: {ev['nome']}, Data: {ev['data']}, Hora: {ev['horario']}")
    else:
        print("Nenhum evento encontrado.")

    # Buscar por ID
    print("\n3. Buscando evento por ID...")
    if ev1_id:
        evento_buscado = buscar_evento_por_id(ev1_id)
        if evento_buscado:
            # A conversão para date/time é feita dentro de buscar_evento_por_id
            print(f"Evento encontrado: {evento_buscado['nome']}, Data: {evento_buscado['data']}")
        else:
            print(f"Evento ID {ev1_id} não encontrado.")

    # Atualizar
    print("\n4. Atualizando evento...")
    if ev2_id:
        atualizado = atualizar_evento(ev2_id, "Workshop Python Masterclass SQLite", "Online via Meet", date(2025, 7, 16), time(10, 0), "Imersão completa em Python e SQLite.")
        if atualizado:
            evento_verificado = buscar_evento_por_id(ev2_id)
            print(f"Evento atualizado: {evento_verificado}")

    # Deletar
    print("\n5. Deletando evento...")
    if ev3_id:
        deletado = deletar_evento(ev3_id)
        if deletado:
            print(f"Evento ID {ev3_id} deletado.")
            evento_deletado = buscar_evento_por_id(ev3_id)
            if not evento_deletado:
                print("Confirmação: Evento não encontrado após deleção.")

    print("\n--- Testes do modelo Evento (SQLite) concluídos ---")

