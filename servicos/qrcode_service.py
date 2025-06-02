import qrcode
import os
from PIL import Image

# Diretório para salvar os QR Codes
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
QRCODE_DIR = os.path.join(BASE_DIR, "dados", "qrcodes")


def gerar_qrcode(dados, nome_arquivo_base, tipo="dados"):
    """Gera um QR Code e salva como imagem PNG.

    Args:
        dados (str): A informação a ser codificada (dados diretos ou URL).
        nome_arquivo_base (str): O nome base para o arquivo PNG (sem extensão).
                                  Será usado para criar um nome único, ex: evento_1_convidado_5.
        tipo (str): 'dados' para embutir a string diretamente, 'url' se for um link.

    Returns:
        str: O caminho completo para o arquivo QR Code gerado, ou None se ocorrer erro.
    """
    # Garante que o diretório de QR Codes exista
    os.makedirs(QRCODE_DIR, exist_ok=True)

    # Define o conteúdo do QR Code
    conteudo_qr = dados
    if tipo == "url" and not dados.startswith(("http://", "https://")):
        print(f"Aviso: URL 	\'{dados}	\' não parece válida. Gerando QR Code mesmo assim.")
        # Poderia adicionar validação mais robusta de URL aqui

    # Monta o caminho completo do arquivo
    nome_arquivo = f"{nome_arquivo_base}.png"
    caminho_arquivo = os.path.join(QRCODE_DIR, nome_arquivo)

    try:
        # Cria o objeto QR Code
        qr = qrcode.QRCode(
            version=1, # Controla o tamanho do QR Code (1 a 40)
            error_correction=qrcode.constants.ERROR_CORRECT_L, # Nível de correção de erro (L, M, Q, H)
            box_size=10, # Tamanho de cada "caixa" do QR Code
            border=4, # Espessura da borda (mínimo 4)
        )
        qr.add_data(conteudo_qr)
        qr.make(fit=True)

        # Cria a imagem do QR Code usando Pillow (PIL)
        img = qr.make_image(fill_color="black", back_color="white")

        # Salva a imagem
        img.save(caminho_arquivo)
        print(f"QR Code gerado e salvo em: {caminho_arquivo}")
        return caminho_arquivo

    except Exception as e:
        print(f"Erro ao gerar QR Code para 	\'{nome_arquivo_base}	\': {e}")
        return None

# Exemplo de uso (pode ser removido ou comentado depois)
if __name__ == '__main__':
    print("--- Testando Serviço QR Code ---")

    # 1. Gerar QR Code com dados embutidos
    print("\n1. Gerando QR Code com dados...")
    dados_convite = "Evento: Festa Junina Tech\nConvidado: Alice Silva\nID: 12345"
    path_qr_dados = gerar_qrcode(dados_convite, "teste_dados_alice", tipo="dados")
    if path_qr_dados:
        print(f"QR Code de dados gerado: {path_qr_dados}")

    # 2. Gerar QR Code com URL
    print("\n2. Gerando QR Code com URL...")
    url_confirmacao = "https://exemplo.com/confirmar/evento/1/convidado/5"
    path_qr_url = gerar_qrcode(url_confirmacao, "teste_url_bob", tipo="url")
    if path_qr_url:
        print(f"QR Code de URL gerado: {path_qr_url}")

    # 3. Teste de erro (nome inválido talvez?)
    # Não há muito como simular erro fácil aqui, exceto talvez permissão de escrita

    print("\n--- Testes do Serviço QR Code concluídos ---")

