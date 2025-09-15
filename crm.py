import pandas as pd
import datetime
import numpy as np
import ccxt
import yfinance as yf 
from datetime import datetime, timedelta

import plotly.graph_objects as c
from plotly.subplots import make_subplots
import plotly.express as px

import scipy.stats as stats

import plotly.graph_objects as go

import streamlit as st

import warnings

# Suppress FutureWarnings
warnings.simplefilter(action='ignore', category=FutureWarning)


st.set_page_config(page_title='Crypto Risk Monitor', layout='wide')


st.title('Crypto Risk Monitor')
st.markdown('##')


# Lista de dicionários
caminhos_data = [
    {'fundo': 'Criptomoedas', 'adm': 'Vortx', 'caminho': r'W:\+Cripto QR\Carteiras\VTR QR '},
    {'fundo': 'Coin Cripto', 'adm': 'BTG', 'caminho': r'W:\+Coin Cripto\Carteiras\Coin Cripto '},
    {'fundo': 'Digital Crypto', 'adm': 'BTG', 'caminho': r'W:\+Digital Crypto\Carteiras\Digital Crypto '},
    {'fundo': 'Essential Crypto', 'adm': 'BTG', 'caminho': r'W:\+Essential Crypto\Carteiras\Essential Crypto '}
]

# Criar DataFrame
caminhos_df = pd.DataFrame(caminhos_data)


fundo = st.selectbox(
    "Select the fund:",
    caminhos_df['fundo'].values.tolist(),
)


try: 
    
    # Último dia útil em relação a hoje
    ultimo_dia_util = pd.Timestamp.today() - pd.offsets.BDay(1)

    # Formatar como AAAAMMDD
    ultimo_dia_util_str = ultimo_dia_util.strftime("%Y%m%d")

    adm = caminhos_df.loc[caminhos_df['fundo'] == fundo, 'adm'].iloc[0]
    
    if adm == 'Vortx':

        caminho = (
        caminhos_df.loc[caminhos_df['fundo'] == fundo, 'caminho'].iloc[0] 
        + ultimo_dia_util_str +'-'
        + ".xlsx"
        )

        carteira = pd.read_excel(caminho, sheet_name='RendaVariavel')
        
        # Filtrar linhas onde 'titulo' contém ' USD'
        filtro_usd = carteira['titulo'].str.contains(' USD', na=False)
        ativos_usd = carteira.loc[filtro_usd][['titulo', 'quantidadeLivre']]
        ativos_usd['titulo'] = ativos_usd['titulo'].str.replace(' USD', '', regex=False).str.strip()

        filtro_brl = ~carteira['titulo'].str.contains(' USD', na=False)
        ativos_brl = carteira.loc[filtro_brl, ['titulo', 'quantidadeLivre']].copy()
        ativos_brl.loc[:, 'titulo'] = ativos_brl['titulo'].str.strip()
        
        ativos_brl.columns = ['symbol', 'qty']
        ativos_usd.columns = ['symbol', 'qty']
        
        symbol_list_usd = [x + '/USD' for x in ativos_usd['symbol']]

        symbol_list_brl = [x + '.SA' for x in ativos_brl['symbol']]

        
    else:
        
        caminho = (
        caminhos_df.loc[caminhos_df['fundo'] == fundo, 'caminho'].iloc[0] 
        + ultimo_dia_util_str
        + ".xlsx"
        )
        
        df = pd.read_excel(caminho, sheet_name="Sheet1", header=None)
        
        # 1) Localiza a linha que contém "Acoes"
        linha_inicio = df.index[df.apply(lambda row: row.astype(str).str.contains("Acoes", case=False).any(), axis=1)][0]

        # 2) Cabeçalho está na linha seguinte
        cabecalho = df.iloc[linha_inicio + 1].tolist()

        # 3) Agora pegamos todas as linhas até encontrar a primeira linha vazia após o cabeçalho
        dados = df.iloc[linha_inicio + 2:].copy()
        dados = dados.dropna(how="all")  # remove linhas totalmente vazias

        # 4) Aplica os nomes de coluna
        dados.columns = cabecalho

        # 5) Reseta índice
        acoes = dados.reset_index(drop=True)

        # 2) localizar linhas de "Compromissada Over" e "Titulos_Publicos"
        idx_compromissada = acoes.index[acoes.apply(lambda row: row.astype(str).str.contains("Compromissada Over", case=False).any(), axis=1)]
        idx_titulos = acoes.index[acoes.apply(lambda row: row.astype(str).str.contains("Titulos_Publicos|Títulos Públicos", case=False).any(), axis=1)]


        # 3) escolher a menor linha encontrada (se existir)
        candidatos = []
        if len(idx_compromissada) > 0:
            candidatos.append(idx_compromissada[0])
        if len(idx_titulos) > 0:
            candidatos.append(idx_titulos[0])

        idx_fim = min(candidatos) if candidatos else len(acoes)

        # Cortar df até essa linha
        ativos_brl = acoes.iloc[0:idx_fim].copy()
        ativos_brl = ativos_brl.dropna(how="all", axis=0)
        ativos_brl = ativos_brl.dropna(how="all", axis=1)
        ativos_brl = ativos_brl[['código', 'Quantidade Total']]
        ativos_brl.columns = ['symbol', 'qty']
        ativos_brl['symbol'] = ativos_brl['symbol'].str.strip()
        symbol_list_brl = [x + '.SA' for x in ativos_brl['symbol']]
        symbol_list_usd=None
    
except:
    
    # Último dia útil em relação a hoje
    ultimo_dia_util = pd.Timestamp.today() - pd.offsets.BDay(2)

    # Formatar como AAAAMMDD
    ultimo_dia_util_str = ultimo_dia_util.strftime("%Y%m%d")
    
    adm = caminhos_df.loc[caminhos_df['fundo'] == fundo, 'adm'].iloc[0]
    
    if adm == 'Vortx':

        caminho = (
        caminhos_df.loc[caminhos_df['fundo'] == fundo, 'caminho'].iloc[0] 
        + ultimo_dia_util_str +'-'
        + ".xlsx"
        )

        carteira = pd.read_excel(caminho, sheet_name='RendaVariavel')
        
        # Filtrar linhas onde 'titulo' contém ' USD'
        filtro_usd = carteira['titulo'].str.contains(' USD', na=False)
        ativos_usd = carteira.loc[filtro_usd][['titulo', 'quantidadeLivre']]
        ativos_usd['titulo'] = ativos_usd['titulo'].str.replace(' USD', '', regex=False).str.strip()

        filtro_brl = ~carteira['titulo'].str.contains(' USD', na=False)
        ativos_brl = carteira.loc[filtro_brl, ['titulo', 'quantidadeLivre']].copy()
        ativos_brl.loc[:, 'titulo'] = ativos_brl['titulo'].str.strip()
        
        ativos_brl.columns = ['symbol', 'qty']
        ativos_usd.columns = ['symbol', 'qty']
        
        symbol_list_usd = [x + '/USD' for x in ativos_usd['symbol']]

        symbol_list_brl = [x + '.SA' for x in ativos_brl['symbol']]

    
    else:
        
        caminho = (
        caminhos_df.loc[caminhos_df['fundo'] == fundo, 'caminho'].iloc[0] 
        + ultimo_dia_util_str
        + ".xlsx"
        )
        
        df = pd.read_excel(caminho, sheet_name="Sheet1", header=None)
        
        # 1) Localiza a linha que contém "Acoes"
        linha_inicio = df.index[df.apply(lambda row: row.astype(str).str.contains("Acoes", case=False).any(), axis=1)][0]

        # 2) Cabeçalho está na linha seguinte
        cabecalho = df.iloc[linha_inicio + 1].tolist()

        # 3) Agora pegamos todas as linhas até encontrar a primeira linha vazia após o cabeçalho
        dados = df.iloc[linha_inicio + 2:].copy()
        dados = dados.dropna(how="all")  # remove linhas totalmente vazias

        # 4) Aplica os nomes de coluna
        dados.columns = cabecalho

        # 5) Reseta índice
        acoes = dados.reset_index(drop=True)

        # 2) localizar linhas de "Compromissada Over" e "Titulos_Publicos"
        idx_compromissada = acoes.index[acoes.apply(lambda row: row.astype(str).str.contains("Compromissada Over", case=False).any(), axis=1)]
        idx_titulos = acoes.index[acoes.apply(lambda row: row.astype(str).str.contains("Titulos_Publicos|Títulos Públicos", case=False).any(), axis=1)]


        # 3) escolher a menor linha encontrada (se existir)
        candidatos = []
        if len(idx_compromissada) > 0:
            candidatos.append(idx_compromissada[0])
        if len(idx_titulos) > 0:
            candidatos.append(idx_titulos[0])

        idx_fim = min(candidatos) if candidatos else len(acoes)

        # Cortar df até essa linha
        ativos_brl = acoes.iloc[0:idx_fim].copy()
        ativos_brl = ativos_brl.dropna(how="all", axis=0)
        ativos_brl = ativos_brl.dropna(how="all", axis=1)
        ativos_brl = ativos_brl[['código', 'Quantidade Total']]
        ativos_brl.columns = ['symbol', 'qty']
        ativos_brl['symbol'] = ativos_brl['symbol'].str.strip()
        symbol_list_brl = [x + '.SA' for x in ativos_brl['symbol']]
        symbol_list_usd=None




if symbol_list_usd==None:
    
    pass

else:

    kraken = ccxt.kraken()

    timeframe = '1d'
    limit = 365

    dfs = []
    for symbol in symbol_list_usd:
        try:
            ohlcv = kraken.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

            df = pd.DataFrame([
                {
                    'date': pd.to_datetime(entry[0], unit='ms'),
                    'symbol': symbol,
                    'open': entry[1],
                    'high': entry[2],
                    'low': entry[3],
                    'close': entry[4],
                    'volume': entry[5],
                }
                for entry in ohlcv
            ])
            dfs.append(df)

        except Exception as e:
            pass

    # Concatenar tudo em um único DataFrame
    ohlcv_coins = pd.concat(dfs, ignore_index=True)

    price_usd = ohlcv_coins[['date', 'symbol', 'close']].pivot_table(index='date', columns='symbol', values='close', aggfunc='mean')


    volume_usd = ohlcv_coins[['date', 'symbol', 'volume']].pivot_table(index='date', columns='symbol', values='volume', aggfunc='mean')




since = datetime.today().date() - timedelta(days=365)

ohlcv_brl = yf.download(symbol_list_brl, start=since)

price_brl = ohlcv_brl['Close'].ffill()

volume_brl = ohlcv_brl['Volume'].fillna(0)

usdbrl = yf.download('BRL=X', start=since)['Close']


usd = st.toggle("USD-denominated")

st.markdown('##')


if symbol_list_usd==None:
    
    if usd:
        price_adj = price_brl.div(usdbrl['BRL=X'], axis=0)
    
    else:
        price_adj = price_brl
    


else:
    
    if usd:

        price_brl_adj = price_brl.div(usdbrl['BRL=X'], axis=0)
        price_adj = pd.concat([price_brl_adj, price_usd], axis=1).ffill()

    else:

        usdbrl_aligned = usdbrl.reindex(price_usd.index).ffill()

        price_usd_adj = price_usd.mul(usdbrl_aligned['BRL=X'], axis=0)

        price_adj = pd.concat([price_brl, price_usd_adj], axis=1).ffill()



# Remove o sufixo '/USD'
price_adj.columns = price_adj.columns.str.replace('/USD', '', regex=False)

# Remove o sufixo '.SA'
price_adj.columns = price_adj.columns.str.replace('.SA', '', regex=False)


def returns_heatmap(df, classe):
        janelas = ['1D', '3D', '1W', '2W', '1M', '3M', '6M', '1Y']
        matriz = pd.DataFrame(columns=janelas, index=df.columns)

#         df_2y = df.ffill().pct_change(520).iloc[-1]
        df_1y = df.ffill().pct_change(260).iloc[-1]
        df_6m = df.ffill().pct_change(130).iloc[-1]
        df_3m = df.ffill().pct_change(60).iloc[-1]
        df_1m = df.ffill().pct_change(20).iloc[-1]
        df_2w = df.ffill().pct_change(10).iloc[-1]
        df_1w = df.ffill().pct_change(5).iloc[-1]
        df_3d = df.ffill().pct_change(3).iloc[-1]
        df_1d = df.ffill().pct_change(1).iloc[-1]


        matriz['1D'] = df_1d
        matriz['3D'] = df_3d
        matriz['1W'] = df_1w
        matriz['2W'] = df_2w
        matriz['1M'] = df_1m
        matriz['3M'] = df_3m
        matriz['6M'] = df_6m
        matriz['1Y'] = df_1y
#         matriz['2Y'] = df_2y
        
        matriz = matriz.dropna()
        
        annotations = []
        for y, row in enumerate(matriz.values):
            for x, val in enumerate(row):
                annotations.append({
                    "x": matriz.columns[x],
                    "y": matriz.index[y],
                    "font": {"color": "black"},
                    "text": f"{val:.2%}",
                    "xref": "x1",
                    "yref": "y1",
                    "showarrow": False
                })
        
        fig = go.Figure(data=go.Heatmap(
                        z=matriz.values,
                        x=matriz.columns.tolist(),
                        y=matriz.index.tolist(),
                        colorscale='RdYlGn',
                        zmin=matriz.values.min(), zmax=matriz.values.max(),  # para garantir que o 0 seja neutro em termos de cor
                        hoverongaps = False,
            text=matriz.apply(lambda x: x.map(lambda y: f"{y:.2%}")),
            hoverinfo='y+x+text',
            showscale=True,
            colorbar_tickformat='.2%'
        ))
        
        
        fig.update_layout(title=classe, annotations=annotations, width=1100,  # Largura do gráfico
    height=800  # Altura do gráfico
)
        fig.show()



def z_score(returns, window=21):
    """
    Calcula o Z-score dos retornos de um ativo considerando uma janela de 1 mês (~21 dias úteis).
    
    :param returns: Série de retornos diários do ativo.
    :param window: Número de dias para calcular média e desvio padrão (default = 21).
    :return: Série com os valores do Z-score ao longo do tempo.
    """
    
    
    rolling_mean = returns.rolling(window).mean()
    rolling_std = returns.rolling(window).std(ddof=0)  # ddof=0 para população, use ddof=1 para amostra
    z_scores = (returns - rolling_mean) / rolling_std
    return z_scores


def compute_percentile(vol, window=252):
    """
    Computes the percentile of the last value in each column relative to the column's distribution.

    :param vol_1m: DataFrame of time series.
    :return: Series containing the percentile of the last value in each column.
    """
    
    vol = vol[-window:]
    percentiles = vol.apply(lambda col: stats.percentileofscore(col.dropna(), col.iloc[-1], kind="rank"))
    return percentiles


if symbol_list_usd==None:
    positions = ativos_brl

else:
    positions = pd.concat([ativos_brl, ativos_usd], axis=0)

positions.index = positions['symbol']

positions = positions.drop(columns=['symbol'])

positions['price'] = price_adj.iloc[-1]

positions ['weights'] = (positions['price'] * positions['qty']) / (positions['price'] * positions['qty']).sum()

positions = positions[(positions['price'] * positions['qty']) > 100]

positions = positions.dropna()

daily_returns = price_adj[positions.index].pct_change()

price_adj = price_adj[positions.index].pct_change()

cov_matrix = daily_returns[-30:].cov().to_numpy()

w = positions ['weights'].to_numpy()

# risco total da carteira
sigma_p = np.sqrt(w.T @ cov_matrix @ w)

# marginal risk contribution
mrc = (cov_matrix @ w) / sigma_p

# absolute risk contributions
rc = w * mrc

# percentual
rc_pct = rc / sigma_p

positions['risk_contribution'] = rc_pct




#Daily Change

daily_change = daily_returns.iloc[-1]


z_score_1d = round(z_score(daily_returns, window=30).iloc[-1].dropna().sort_values(), 2)


# Z-score

z_score_1w = round(z_score(daily_returns, window=7).iloc[-1].dropna().sort_values(), 2)

z_score_1m = round(z_score(daily_returns, window=30).iloc[-1].dropna().sort_values(), 2)

z_score_3m = round(z_score(daily_returns, window=90).iloc[-1].dropna().sort_values(), 2)

z_score_12m = round(z_score(daily_returns, window=360).iloc[-1].dropna().sort_values(), 2)


# Returns

returns_1w = price_adj.pct_change(7).iloc[-1].dropna().sort_values()

returns_1m = price_adj.pct_change(30).iloc[-1].dropna().sort_values()

returns_3m = price_adj.pct_change(90).iloc[-1].dropna().sort_values()

returns_12m = price_adj.pct_change(360).iloc[-1].dropna().sort_values()



# Volatility

vol_1w = daily_returns.ewm(span=7).std() * np.sqrt(365)

vol_1m = daily_returns.ewm(span=30).std() * np.sqrt(365)

vol_3m = daily_returns.ewm(span=90).std() * np.sqrt(365)

vol_12m = daily_returns.ewm(span=360).std() * np.sqrt(365)



# Vol Percentile

vp_1w = round(compute_percentile( vol_1m, window=180))

vp_1m = round(compute_percentile( vol_1m, window=360))

vp_3m = round(compute_percentile( vol_3m, window=520))

vp_12m = round(compute_percentile( vol_12m, window=len(vol_12m)))



# Criando um MultiIndex para organizar os índices acima das colunas
multi_index = pd.MultiIndex.from_tuples([
    ("Price", "Last"),
    ("Price", "Daily Change"),
    ("Price", "Z-Score"),
    
    ("Returns", "1 W"),
    ("Returns", "1 M"),
    ("Returns", "3 M"),
    ("Returns", "12 M"),
    
    ("Z-Score", "1 W"),
    ("Z-Score", "1 M"),
    ("Z-Score", "3 M"),
    ("Z-Score", "12 M"),
    
    ("Realized Volatility", "1 W"),
    ("Realized Volatility", "1 M"),
    ("Realized Volatility", "3 M"),
    ("Realized Volatility", "12 M"),
    
    ("RV Percentile", "1 W"),
    ("RV Percentile", "1 M"),
    ("RV Percentile", "3 M"),
    ("RV Percentile", "12 M"),
])

# Criando o DataFrame com MultiIndex nas colunas
risk_metrics = pd.DataFrame([
    price_adj.iloc[-1],
    daily_change,
    z_score_1d,
    
    returns_1w,
    returns_1m,
    returns_3m,
    returns_12m,
    
    round(z_score_1w, 2),
    round(z_score_1m, 2),
    round(z_score_3m, 2),
    round(z_score_12m, 2),
    
    vol_1w.iloc[-1].dropna(),
    vol_1m.iloc[-1].dropna(),
    vol_3m.iloc[-1].dropna(),
    vol_12m.iloc[-1].dropna(),
    
    round(vp_1w),
    round(vp_1m),
    round(vp_3m),
    round(vp_12m)
]).T

# Atribuindo os MultiIndex às colunas
risk_metrics.columns = multi_index

# risk_metrics = risk_metrics.dropna()

risk_metrics_temp = risk_metrics.copy()

cols_to_format = [
    ("Price", "Daily Change"),
    ("Returns", "1 W"), ("Returns", "1 M"), ("Returns", "3 M"), ("Returns", "12 M"),
    ("Realized Volatility", "1 W"), ("Realized Volatility", "1 M"), 
    ("Realized Volatility", "3 M"), ("Realized Volatility", "12 M")
]

for col in cols_to_format:
    risk_metrics[col] = risk_metrics[col].apply(lambda x: f"{x:.2%}")
    
    
cols_to_format = [
    ("Price", "Last"), ("Price", "Z-Score"),
    ("Z-Score", "1 W"), ("Z-Score", "1 M"), ("Z-Score", "3 M"), ("Z-Score", "12 M"),
    ("RV Percentile", "1 W"), ("RV Percentile", "1 M"), 
    ("RV Percentile", "3 M"), ("RV Percentile", "12 M")
]

for col in cols_to_format:
    risk_metrics[col] = risk_metrics[col].apply(lambda x: f"{x:.2f}")



risk_metrics



col1, col2 = st.columns(2)

with col1:

    weights_sorted = positions['weights'].sort_values()

    # cria uma paleta
    palette = px.colors.qualitative.Set3

    # cria um dicionário ativo → cor
    assets = positions.index.tolist()
    color_map = {asset: palette[i % len(palette)] for i, asset in enumerate(assets)}

    # aplica as cores de acordo com o ativo
    colors = [color_map[asset] for asset in weights_sorted.index]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=weights_sorted.index,
        y=weights_sorted,
        marker_color=colors
    ))

    fig.update_layout(
        title="Portfolio Weights",
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(tickmode='linear', tickangle=-45)
    )

    fig.update_yaxes(tickformat=".2%")
    st.plotly_chart(fig)


with col2:

    # ordena por risk contribution
    weights_sorted = positions['risk_contribution'].sort_values()

    # gráfico
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=weights_sorted.index,
        y=weights_sorted,
        marker_color=colors
    ))

    fig.update_layout(
        title="Risk Contribution",
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(tickmode='linear', tickangle=-45)
    )

    fig.update_yaxes(tickformat=".2%")
    st.plotly_chart(fig)



col3, col4 = st.columns(2)

with col3:

    hist_vol = daily_returns.ewm(span=35).std() * np.sqrt(365)

    fig = px.line(
        hist_vol,
            title="Historical Volatility"
        )

    fig.update_layout(
        xaxis_title="",
        yaxis_title="")

    fig.update_yaxes(tickformat=".2%")

    fig.update_layout( width=600,  # Largura do gráfico
                height=500  # Altura do gráfico
            )


    fig.update_layout(
    legend=dict(
        orientation="h",
        x=0.5, xanchor="center",
        y=-0.5, yanchor="bottom"   # base da legenda colada na base do plot
    ),
    margin=dict(b=70)            # espaço pros rótulos do eixo X
    )

    st.plotly_chart(fig)



with col4:

    # Ordenando os valores de Z-Score
    sorted_z_score = risk_metrics_temp[("Price", "Z-Score")].sort_values()

    # Definindo cores com base nos valores de Z-Score
    colors = ['red' if x < 0 else 'green' for x in sorted_z_score]

    # Criando o gráfico de barras com todos os rótulos visíveis
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=sorted_z_score.index,
        y=sorted_z_score,
        marker_color=colors
    ))

    # Ajustando o layout para exibir todos os rótulos
    fig.update_layout(
        title="Monthly Returns Move Size",
        xaxis_title="",
        yaxis_title="Move Size",
        xaxis=dict(tickmode='linear', tickangle=-45)
    )


    st.plotly_chart(fig)
