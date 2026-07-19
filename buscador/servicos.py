from google import genai

# Injeção direta da chave (temporário para teste)
CHAVE_API = "sua_chave_aqui"
# Inicializa o motor
cliente = genai.Client(api_key=CHAVE_API)

def analisar_preco_com_ia(nome_produto):
    """
    Envia o nome do produto para o Gemini e retorna a análise de mercado.
    """
    prompt = f"Atue como um especialista em ofertas de mercado. Faça uma estimativa de preço médio atual e diga se é um bom momento para comprar o produto: {nome_produto}. Responda de forma curta e objetiva."
    
    try:
        resposta = cliente.models.generate_content(
            model='gemini-2.0-flash', # <-- SÓ MUDAR ESTE NOME
            contents=prompt
        )
        return resposta.text
    except Exception as e:
        return f"Erro ao consultar a IA: {e}"