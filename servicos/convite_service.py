# -*- coding: utf-8 -*-
import os
import datetime # Importar o módulo datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# Diretório para salvar os PDFs dos convites
CONVITE_DIR = "/home/ubuntu/convite_qrcode/dados/convites"

def gerar_convite_pdf(evento, convidado, caminho_qrcode, nome_arquivo_base):
    """Gera um convite em PDF com dados do evento, convidado e QR Code.

    Args:
        evento (dict): Dicionário com os dados do evento (nome, local, data, horario, etc.).
                       Espera-se que data e horario sejam objetos date/time ou strings formatadas.
        convidado (dict): Dicionário com os dados do convidado (nome, email, etc.).
        caminho_qrcode (str): O caminho completo para a imagem do QR Code gerada.
        nome_arquivo_base (str): Nome base para o arquivo PDF (ex: evento_1_convidado_5).

    Returns:
        str: O caminho completo para o arquivo PDF gerado, ou None se ocorrer erro.
    """
    # Garante que o diretório de convites exista
    os.makedirs(CONVITE_DIR, exist_ok=True)

    # Monta o caminho completo do arquivo PDF
    nome_arquivo = f"{nome_arquivo_base}.pdf"
    caminho_pdf = os.path.join(CONVITE_DIR, nome_arquivo)

    try:
        c = canvas.Canvas(caminho_pdf, pagesize=letter)
        width, height = letter # Tamanho da página (aprox. 8.5 x 11 polegadas)

        # --- Desenho do Convite ---

        # Título do Evento
        nome_evento = evento.get("nome", "Nome do Evento Indisponível")
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width / 2.0, height - 1.5 * inch, nome_evento)

        # Informações do Evento
        c.setFont("Helvetica", 12)
        y_position = height - 2.5 * inch
        line_height = 0.25 * inch

        # Obtém e tenta formatar Data e Hora
        data_evento = evento.get("data")
        horario_evento = evento.get("horario")

        # Tenta converter strings para objetos date/time se necessário
        if isinstance(data_evento, str):
            try: data_evento = datetime.datetime.strptime(data_evento, "%Y-%m-%d").date()
            except (ValueError, TypeError): data_evento = None # Mantém None se falhar
        if isinstance(horario_evento, str):
            try: horario_evento = datetime.datetime.strptime(horario_evento, "%H:%M").time()
            except (ValueError, TypeError): horario_evento = None # Mantém None se falhar

        # Verifica os tipos usando type() diretamente
        data_formatada = data_evento.strftime("%d/%m/%Y") if type(data_evento) is datetime.date else str(data_evento or "Data não definida")
        horario_formatado = horario_evento.strftime("%H:%M") if type(horario_evento) is datetime.time else str(horario_evento or "Horário não definido")
        local_evento = evento.get("local", "Local não definido")

        c.drawString(1 * inch, y_position, f"Data: {data_formatada}")
        y_position -= line_height
        c.drawString(1 * inch, y_position, f"Horário: {horario_formatado}")
        y_position -= line_height
        c.drawString(1 * inch, y_position, f"Local: {local_evento}")
        y_position -= line_height * 1.5 # Espaço maior

        # Informações do Convidado
        nome_convidado = convidado.get("nome", "Nome do Convidado Indisponível")
        c.setFont("Helvetica-Oblique", 14)
        c.drawString(1 * inch, y_position, "Convidado(a):")
        y_position -= line_height * 0.8
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1.2 * inch, y_position, nome_convidado)
        y_position -= line_height * 2 # Espaço maior

        # QR Code
        try:
            qr_image = ImageReader(caminho_qrcode)
            qr_width = 2 * inch
            qr_height = 2 * inch
            qr_x = width - qr_width - 1 * inch
            qr_y = 1 * inch
            c.drawImage(qr_image, qr_x, qr_y, width=qr_width, height=qr_height, mask="auto")
            c.setFont("Helvetica", 8)
            c.drawRightString(width - 1*inch, qr_y - 0.2*inch, "Apresente este QR Code na entrada")
        except Exception as img_err:
            print(f"Erro ao adicionar QR Code ao PDF: {img_err}")
            c.setFont("Helvetica", 10)
            c.setFillColorRGB(1, 0, 0) # Vermelho
            c.drawString(1 * inch, 1 * inch, "Erro ao carregar QR Code.")

        # Linha de rodapé (opcional)
        c.setFont("Helvetica", 9)
        c.drawCentredString(width / 2.0, 0.75 * inch, "Este convite é pessoal e intransferível.")

        # Salva o PDF
        c.save()
        print(f"Convite PDF gerado e salvo em: {caminho_pdf}")
        return caminho_pdf

    except Exception as e:
        # Tenta obter o nome do convidado para a mensagem de erro
        nome_convidado_erro = convidado.get("nome", "desconhecido") if convidado else "desconhecido"
        # Usando aspas simples para as chaves internas da f-string
        print(f"Erro ao gerar PDF do convite para o convidado \"{nome_convidado_erro}\" (arquivo base: \"{nome_arquivo_base}\"): {e}")
        return None

# Exemplo de uso (pode ser removido ou comentado depois)
if __name__ == "__main__":
    # Adiciona o diretório pai ao path para encontrar qrcode_service
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    try:
        from servicos.qrcode_service import gerar_qrcode # Para gerar um QR de teste
    except ImportError:
        print("Erro: Não foi possível importar qrcode_service. Execute de dentro do diretório raiz.")
        sys.exit(1)

    print("--- Testando Serviço de Geração de Convite PDF ---")

    # 1. Dados de exemplo
    evento_ex = {
        "id": 1,
        "nome": "Conferência Anual de Tecnologia",
        "local": "Centro de Convenções",
        "data": datetime.date(2025, 10, 20), # Usando datetime.date
        "horario": datetime.time(9, 0), # Usando datetime.time
        "descricao": "Palestras e workshops sobre as últimas tendências."
    }
    convidado_ex = {
        "id": 5,
        "evento_id": 1,
        "nome": "Carlos Pereira",
        "email": "carlos.p@email.com",
        "telefone": "(31) 91111-2222",
        "status_presenca": "pendente"
    }
    # Corrigindo f-strings com aspas simples internas manualmente
    nome_base = f"evento_{evento_ex['id']}_convidado_{convidado_ex['id']}"
    dados_qr = f"EventoID:{evento_ex['id']};ConvidadoID:{convidado_ex['id']};Nome:{convidado_ex['nome']}"

    # 2. Gerar um QR Code de teste primeiro
    print("\nGerando QR Code de teste...")
    # Garante que o diretório de dados exista para o qrcode_service
    os.makedirs("/home/ubuntu/convite_qrcode/dados/qrcodes", exist_ok=True)
    caminho_qr_teste = gerar_qrcode(dados_qr, nome_base, tipo="dados")

    # 3. Gerar o PDF do convite
    if caminho_qr_teste:
        print("\nGerando PDF do convite...")
        caminho_pdf_gerado = gerar_convite_pdf(evento_ex, convidado_ex, caminho_qr_teste, nome_base)
        if caminho_pdf_gerado:
            print(f"Convite PDF gerado com sucesso: {caminho_pdf_gerado}")
        else:
            print("Falha ao gerar o PDF do convite.")
    else:
        print("Falha ao gerar QR Code de teste, não é possível gerar o PDF.")

    print("\n--- Testes do Serviço de Convite PDF concluídos ---")

