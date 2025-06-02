# Sistema de Emissão de Convites com QR Code

Este é um sistema CLI (Command Line Interface) para gerenciamento de eventos e convidados, com geração de convites personalizados em PDF contendo QR Codes.

## Funcionalidades

- **Gerenciamento de Eventos**: Criar, listar, editar e excluir eventos
- **Gerenciamento de Convidados**: Criar, listar, editar e excluir convidados
- **Geração de QR Code**: Criação de QR Codes com dados do evento/convidado ou URL externa
- **Geração de Convites**: Criação de PDFs personalizados com dados do evento, convidado e QR Code

## Estrutura do Projeto

```
convite_qrcode/
│-- main.py                         # Ponto de entrada principal (menu e fluxo)
│-- db/
│   └── conexao.py                  # Conexão com o banco de dados (SQLite/MySQL)
│-- modelos/
│   ├── evento.py                   # Classe/modelo e operações de Evento
│   └── convidado.py                # Classe/modelo e operações de Convidado
│-- servicos/
│   ├── qrcode_service.py           # Lógica de geração de QR Code
│   └── convite_service.py          # Geração do convite PDF
│-- dados/
│   ├── qrcodes/                    # Imagens de QR Codes gerados
│   └── convites/                   # PDFs dos convites gerados
│-- requirements.txt                # Dependências do projeto
```

## Requisitos

- Python 3.6+
- Bibliotecas listadas em `requirements.txt`

## Configuração e Instalação

1. Clone o repositório ou extraia os arquivos
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Execute o programa:

```bash
python main.py
```

## Banco de Dados

O sistema está configurado para usar SQLite por padrão, armazenando o banco de dados em `dados/convites_db.sqlite`. Para usar MySQL:

1. Descomente o código MySQL em `db/conexao.py`
2. Comente o código SQLite
3. Configure as variáveis de ambiente ou edite diretamente as credenciais:
   - `DB_HOST`: Host do servidor MySQL (padrão: "localhost")
   - `DB_USER`: Usuário do MySQL
   - `DB_PASSWORD`: Senha do MySQL
   - `DB_NAME`: Nome do banco de dados (padrão: "convites_db")

## Uso

O sistema apresenta um menu interativo no terminal com as seguintes opções:

1. **Menu de Eventos**

   - Criar Novo Evento
   - Listar Todos os Eventos
   - Editar Evento Existente
   - Excluir Evento Existente

2. **Menu de Convidados**

   - Criar Novo Convidado (e gerar convite)
   - Listar Convidados por Evento
   - Listar Todos os Convidados
   - Editar Convidado Existente
   - Excluir Convidado Existente

3. **Geração de Convites**
   - Ao criar um convidado, você pode gerar o convite imediatamente
   - Escolha entre QR Code com dados embutidos ou URL externa

## Arquivos Gerados

- QR Codes: Salvos em `dados/qrcodes/`
- Convites PDF: Salvos em `dados/convites/`

## Observações Importantes

- O sistema usa SQLite por padrão para facilitar testes sem configuração adicional
- A estrutura foi projetada para permitir fácil troca entre SQLite e MySQL
- Os convites gerados incluem nome do evento, data, horário, local, nome do convidado e QR Code
- O QR Code pode conter dados do evento/convidado ou uma URL externa (ex: sistema de confirmação)

# Gerador_Convite_QRCode

## Este projeto foi idealizado e desenvolvido por:

Vanthuir Maia
📧 vanthuir.dev@gmail.com

Fique à vontade para entrar em contato para sugestões, melhorias ou colaborações futuras.
