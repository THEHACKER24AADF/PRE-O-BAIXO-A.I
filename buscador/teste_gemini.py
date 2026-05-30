from google import genai
import os

# 1. Leitura na Força Bruta (ignorando a biblioteca que bugou)
caminho_env = ".env"
CHAVE_API = None

try:
    # O Python abre o arquivo, acha o "=", pega o lado direito e limpa as aspas!
    with open(caminho_env, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            if "CHAVE_API=" in linha:
                CHAVE_API = linha.split("=")[1].strip().replace('"', '').replace("'", "")
except Exception as e:
    print(f"Erro ao ler o arquivo na unha: {e}")

if not CHAVE_API:
    print("❌ A extração falhou. A variável continuou vazia.")
    exit()

print("✅ Chave extraída na força bruta com sucesso! Conectando com a IA...\n")

# 2. Inicializa a IA com a chave que nós mesmos capturamos
cliente = genai.Client(api_key=CHAVE_API)

resposta = cliente.models.generate_content(
    model='gemini-2.5-flash',
    contents="Aja como um assistente de e-commerce. Diga uma frase curta confirmando que o cérebro do Preço Baixo A.I. está blindado e pronto para buscar ofertas."
)

print("--- RESPOSTA DA IA ---")
print(resposta.text)