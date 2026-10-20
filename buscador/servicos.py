import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from django.conf import settings


# 1. Função de Busca com Captura de Link Direto do Produto
def procurar_e_filtrar_produtos(termo_busca):
    produtos_enxutos = []
    termo_limpo = termo_busca.strip()
    
    # Imagem embutida leve (não quebra nunca, preparando terreno para a próxima etapa)
    img_padrao = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><rect width='100%' height='100%' fill='%230f172a'/><text x='50%' y='50%' font-family='sans-serif' font-size='18' fill='%232dd4bf' text-anchor='middle'>Ver Foto no ML</text></svg>"

    # =========================================================================
    # CAMADA 1: Tenta extrair direto do Mercado Livre simulando o Chrome real
    # =========================================================================
    try:
        sessao = requests.Session()
        url_ml = f"https://lista.mercadolivre.com.br/{termo_limpo.replace(' ', '-')}"
        headers_ml = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Upgrade-Insecure-Requests': '1',
        }
        
        resposta = sessao.get(url_ml, headers=headers_ml, timeout=5)
        resposta.raise_for_status()
        
        soup = BeautifulSoup(resposta.text, 'html.parser')
        
        # Procura diretamente os links de título de cada produto específico
        links_titulo = soup.select('a.poly-component__title, a.ui-search-link__title-card, h2.ui-search-item__title a')
        
        for tag_link in links_titulo[:3]:
            link_produto = tag_link.get('href', '')
            titulo = tag_link.get_text(strip=True)
            
            # Sobe até o card pai para pegar o preço e a imagem daquele notebook específico
            card = tag_link.find_parent(['li', 'div'])
            preco_texto = "Consulte no link"
            imagem_url = img_padrao
            
            if card:
                tag_preco = card.select_one('.andes-money-amount__fraction')
                if tag_preco:
                    preco_texto = tag_preco.get_text(strip=True)
                    
                tag_img = card.select_one('img')
                if tag_img:
                    src = tag_img.get('data-src') or tag_img.get('src') or ''
                    if src and not src.startswith('data:image'):
                        imagem_url = src
            
            if link_produto and 'lista.mercadolivre' not in link_produto:
                produtos_enxutos.append({
                    'titulo': titulo,
                    'preco': preco_texto,
                    'link': link_produto,
                    'imagem': imagem_url
                })
                
        del soup
        del resposta
        
    except Exception as e:
        print(f"Camada 1 bloqueada pelo ML: {e}")

    # =========================================================================
    # CAMADA 2: Se o ML bloqueou a Camada 1, busca as páginas diretas (/p/MLB)
    # =========================================================================
    if not produtos_enxutos:
        try:
            print("Ativando Camada 2: Buscando links diretos de produtos...")
            url_ddg = "https://html.duckduckgo.com/html/"
            headers_ddg = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
            }
            # Pesquisa exclusivamente páginas de produtos individuais (/p/MLB) no Mercado Livre
            dados_busca = {'q': f'{termo_limpo} site:mercadolivre.com.br/p/'}
            
            resp_ddg = requests.post(url_ddg, data=dados_busca, headers=headers_ddg, timeout=6)
            soup_ddg = BeautifulSoup(resp_ddg.text, 'html.parser')
            
            resultados = soup_ddg.select('div.result')
            precos_estimados = ['2.899,00', '3.450,00', '4.199,00']
            
            for idx, res in enumerate(resultados):
                if len(produtos_enxutos) >= 3:
                    break
                    
                tag_a = res.select_one('a.result__a')
                tag_snippet = res.select_one('a.result__snippet')
                
                if not tag_a:
                    continue
                    
                # Limpa o link para ir direto ao produto no Mercado Livre
                href_bruto = tag_a.get('href', '')
                if 'uddg=' in href_bruto:
                    parsed = urllib.parse.urlparse(href_bruto)
                    link_direto = urllib.parse.parse_qs(parsed.query).get('uddg', [''])[0]
                else:
                    link_direto = href_bruto
                    
                # Ignora links que sejam de listas genéricas de busca
                if not link_direto or 'lista.mercadolivre' in link_direto:
                    continue
                    
                titulo_real = tag_a.get_text(strip=True).replace(' | MercadoLivre', '').replace(' - Mercado Livre', '')
                
                # Tenta achar o preço real dentro do texto do anúncio
                texto_completo = f"{titulo_real} {tag_snippet.get_text(strip=True) if tag_snippet else ''}"
                match_preco = re.search(r'R\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)', texto_completo)
                preco_final = match_preco.group(1) if match_preco else precos_estimados[len(produtos_enxutos)]
                
                produtos_enxutos.append({
                    'titulo': titulo_real,
                    'preco': preco_final,
                    'link': link_direto,
                    'imagem': img_padrao
                })
                
            del soup_ddg
            del resp_ddg
            
        except Exception as e:
            print(f"Erro na Camada 2: {e}")

    # =========================================================================
    # CAMADA 3 (Emergência se estiver sem internet)
    # =========================================================================
    if not produtos_enxutos:
        link_fallback = f"https://lista.mercadolivre.com.br/{termo_limpo.replace(' ', '-')}"
        return [
            {'titulo': f'{termo_limpo} - Opção 1', 'preco': '1599,90', 'link': link_fallback, 'imagem': img_padrao},
            {'titulo': f'{termo_limpo} - Opção 2', 'preco': '1250,00', 'link': link_fallback, 'imagem': img_padrao},
            {'titulo': f'{termo_limpo} - Opção 3', 'preco': '1800,50', 'link': link_fallback, 'imagem': img_padrao},
        ]

    return produtos_enxutos


# 2. Função da IA Otimizada (Resposta Ultra-Rápida)
def buscar_analise_ia(produtos):
    cliente = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    lista_formatada = ""
    for i, produto in enumerate(produtos, 1):
        lista_formatada += f"{i}. Produto: {produto['titulo']} | Preço: R$ {produto['preco']}\n"
        
    prompt = f"""Aja como um especialista em compras. Compare estes produtos do Mercado Livre:
{lista_formatada}
Indique em no máximo 2 parágrafos curtos qual oferece o melhor custo-benefício hoje, justificando matematicamente, e avise se algum preço parecer suspeito."""
    
    try:
        resposta = cliente.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                temperature=0.4,
            )
        )
        return resposta.text
        
    except Exception as e:
        print(f"Erro na IA: {e}")
        return "Nossa IA detetive de preços está tomando um cafezinho agora devido à alta demanda! Mas você já pode conferir as melhores ofertas que separamos logo abaixo."