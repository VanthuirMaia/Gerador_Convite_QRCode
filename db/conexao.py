# -*- coding: utf-8 -*-
import sqlite3
import os

# Define o nome do arquivo do banco de dados SQLite
DB_NAME = "convites_db.sqlite"
DB_PATH = os.path.join("/home/ubuntu/convite_qrcode/dados", DB_NAME)

def criar_conexao():
    """Cria e retorna uma conexão com o banco de dados SQLite."""
    conexao = None
    try:
        # Garante que o diretório de dados exista
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conexao = sqlite3.connect(DB_PATH)
        # Para retornar dicionários em vez de tuplas (opcional, mas útil)
        conexao.row_factory = sqlite3.Row
        # Habilita chaves estrangeiras (importante para ON DELETE CASCADE)
        conexao.execute("PRAGMA foreign_keys = ON;")
        # print(f"Conexão com o banco de dados SQLite 	\" {DB_PATH}	\" estabelecida.")
        return conexao
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao SQLite: {e}")
        return None

def fechar_conexao(conexao):
    """Fecha a conexão com o banco de dados."""
    if conexao:
        conexao.close()
        # print("Conexão com o SQLite fechada.")

def inicializar_banco():
    """Cria as tabelas no banco de dados SQLite se não existirem."""
    conexao = criar_conexao()
    if not conexao:
        return

    cursor = conexao.cursor()
    try:
        # Criação da tabela Eventos (SQLite syntax)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            local TEXT,
            data TEXT, -- SQLite não tem tipo DATE nativo, usar TEXT (YYYY-MM-DD)
            horario TEXT, -- Usar TEXT (HH:MM)
            descricao TEXT
        );
        """)
        # print("Tabela 	\"eventos	\" verificada/criada.")

        # Criação da tabela Convidados (SQLite syntax)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS convidados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evento_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            email TEXT UNIQUE,
            telefone TEXT,
            status_presenca TEXT CHECK(status_presenca IN ('pendente', 'presente', 'ausente')) DEFAULT 'pendente',
            FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE
        );
        """)
        # print("Tabela 	\"convidados	\" verificada/criada.")

        conexao.commit()
    except sqlite3.Error as e:
        print(f"Erro ao criar tabelas SQLite: {e}")
        conexao.rollback()
    finally:
        cursor.close()
        fechar_conexao(conexao)

# --- Código de Conexão MySQL (Mantido para referência) ---
"""
import mysql.connector
from mysql.connector import Error
import os

# Idealmente, buscar de variáveis de ambiente ou arquivo de configuração
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root") # Substitua por seu usuário
DB_PASSWORD = os.getenv("DB_PASSWORD", "") # Substitua por sua senha
DB_NAME_MYSQL = os.getenv("DB_NAME", "convites_db") # Nome do banco de dados MySQL

def criar_conexao_mysql():
    # ... (código original do MySQL aqui) ...
    pass

def fechar_conexao_mysql(conexao):
    # ... (código original do MySQL aqui) ...
    pass

def inicializar_banco_mysql():
    # ... (código original do MySQL aqui) ...
    pass
"""

# Exemplo de uso (pode ser removido ou comentado depois)
if __name__ == "__main__":
    print("Inicializando o banco de dados SQLite...")
    inicializar_banco()
    print("Verificação/Criação do banco de dados e tabelas SQLite concluída.")
    # Teste de conexão
    # conexao_teste = criar_conexao()
    # if conexao_teste:
    #     fechar_conexao(conexao_teste)

