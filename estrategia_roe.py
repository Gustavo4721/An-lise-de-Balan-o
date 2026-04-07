import requests
import pandas as pd
import yfinance as yf

url = "https://laboratoriodefinancas.com/api/v2"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc2NTEzMTk1LCJpYXQiOjE3NzM5MjExOTUsImp0aSI6ImU2ZGFhM2U5ZGEzMzQzNzJiMzAwMTNmNzNkMTVkNzczIiwidXNlcl9pZCI6IjExMCJ9.aNw1HPkLXRviOgrZmrX7eCp6ZSBv0M-gLcQ6XT3nz2c"

resp = requests.get(
    f"{url}/bolsa/planilhao",
    headers = {"Authorization": f"Bearer {token}"},
    params = {'data_base': '2021-04-01'}
)
dados = resp.json()
df = pd.DataFrame(dados)

# Usamos .copy() para evitar avisos técnicos do pandas
df2 = df[['ticker', 'roic', 'earning_yield']].copy()
df2['rank_roic'] = df2['roic'].rank(ascending = False)
df2['rank_p_ey'] = df2['earning_yield'].rank(ascending = False)
df2['rank_final'] = (df2['rank_roic'] + df2['rank_p_ey']) / 2

# Desafio aplicado: ascending = True seleciona os melhores ranks (menores números)
top_20_tickers = df2.sort_values('rank_final', ascending = True)['ticker'][:20].tolist()

print("As 20 melhores ações selecionadas são:")
print(top_20_tickers)
print("-" * 30)

# API para pegar os preços das ações
retornos_carteira = []
retornos_detalhados = {} # Estrutura adicionada para mapear cada ticker ao seu retorno

# Um laço (loop) para repetir a ação para cada um dos 20 tickers da nossa lista
for ticker in top_20_tickers:
    params = {'ticker': ticker, 'data_ini': '2021-04-01', 'data_fim': '2026-03-31'}
    resp = requests.get(
        f'{url}/preco/corrigido',
        headers = {"Authorization": f"Bearer {token}"},
        params = params
    )
    dados_preco = resp.json()
    
    # Pula a ação se a API não retornar dados para ela
    if not dados_preco:
        continue
        
    df_preco = pd.DataFrame(dados_preco)

    # Filtro inicial
    filtro2 = df_preco['data'] >= '2021-04-01'
    preco_inicial = float(df_preco.loc[filtro2, 'fechamento'].iloc[0])

    # Preço final
    filtro1 = df_preco['data'] <= '2026-03-30'
    preco_final = float(df_preco.loc[filtro1, 'fechamento'].iloc[-1])

    retorno_individual = (preco_final / preco_inicial) - 1
    
    retornos_carteira.append(retorno_individual)
    retornos_detalhados[ticker] = retorno_individual # Associa o retorno à respectiva ação

# Calculando a média da rentabilidade das 20 ações
rentabilidade_total_carteira = sum(retornos_carteira) / len(retornos_carteira)


# API para pegar o Ibov
ibov = yf.download('^BVSP', start = '2021-04-01', end = '2026-03-31')

# Preço inicial
ibov_ini = float(ibov['Close'].iloc[0])

# Preço final
ibov_fim = float(ibov['Close'].iloc[-1])
rentabilidade_total_ibov = (ibov_fim / ibov_ini) - 1

# Impressão dos retornos individuais em formato de lista estruturada
print("Retorno individual das 20 melhores ações (5 anos):")
for ticker, retorno in retornos_detalhados.items():
    print(f"- {ticker}: {retorno * 100:.2f}%")
print("-" * 30)

print(f"Retorno da Carteira (5 anos): {rentabilidade_total_carteira * 100:.2f}%")
print(f"Retorno do Ibovespa (5 anos): {rentabilidade_total_ibov * 100:.2f}%")