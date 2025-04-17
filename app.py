import streamlit as st
from config import conectar_portal
import pandas as pd
import pygwalker as pyg
from pygwalker.api.streamlit import StreamlitRenderer
import datetime
import requests
import os
import duckdb

st.set_page_config(page_title="Painel de Indicadores", layout="wide")
st.title("Tabulação para o Painel de Indicadores")

##################

# Código alternativo para carregar dados sem API ArcGIS
#@st.cache_data
#def baixar_arquivo():
#    url = "https://raw.githubusercontent.com/R-Giacomin/Painel_PNDR/main/data/dados_reduzido.db"
#    file_path = "dados_reduzido.db"
#    if not os.path.exists(file_path):
#        response = requests.get(url, stream=True)
#        response.raise_for_status()
#        with open(file_path, 'wb') as f:
#            for chunk in response.iter_content(chunk_size=8192):
#                f.write(chunk)
#    return file_path

#@st.cache_data
#def carregar_dados():
#    file_path = baixar_arquivo()

    # Connect to the database
#    con = duckdb.connect(database=file_path, read_only=True)

    # Execute the query and fetch the results into a pandas DataFrame
#    query1 = "SELECT * FROM recortes_geograficos"
#    query2 = "SELECT * FROM valoresmeta"
#    recortes_geograficos = con.execute(query1).fetchdf()
#    valoresmeta = con.execute(query2).fetchdf()

    # Close the connection
#    con.close()

#    df = valoresmeta.merge(recortes_geograficos, left_on='geoloc_id', right_on='codigo_ibge', how='left')
#    df = df.dropna(subset=['codigo_ibge'])
#    df = df.drop(columns=['mdata_id',	'geoloc_id',	'local_id', 'geoloc_id', 'local_name'])
#    df = df.rename(columns={'data_name': 'Indicador','orig_name': 'Sigla_indicador' ,'value': 'Valor', 'refdate': 'Ano'})
#    df = df.dropna(subset=['Ano'])
#    df['Ano'] = pd.to_datetime(df['Ano']).dt.year.astype(int)
#    return df

#with st.spinner("Carregando dados, esse processo pode levar alguns minutos..."):
#    df = carregar_dados()

###############

# Código para carregar dados via API ArcGIS

@st.cache_data
# Limitado a Região Norte e anos de 2021 a 2022
def carregar_valores_df(inicio='2022-01-01', fim='2022-12-31'):
    gis = conectar_portal()
    valores_item = gis.content.search("valoresmeta", item_type="Map Image Layer")[0]
    valores_table = valores_item.tables[0]
    valores_set = valores_table.query(
        where=f"refdate >= DATE '{inicio}' AND refdate <= DATE '{fim}' AND geoloc_id < 2000000",
        out_fields="geoloc_id, data_name, value, refdate"
    )
    return pd.DataFrame([f.attributes for f in valores_set.features])

@st.cache_data
def carregar_recortes_df():
    gis = conectar_portal()
    recortes_item = gis.content.search("recortes_geograficos", item_type="Map Image Layer")[0]
    recortes_layer = recortes_item.layers[0]
    valores_set = recortes_layer.query(where="1=1", out_fields="*")
    return pd.DataFrame([f.attributes for f in valores_set.features])

with st.spinner("Carregando dados, esse processo pode levar alguns minutos..."):
    valores_df = carregar_valores_df()
    recortes_df = carregar_recortes_df()
    df = valores_df.merge(recortes_df, left_on='geoloc_id', right_on='codigo_ibge', how='left')
    df = df.dropna(subset=['codigo_ibge'])
    df = df.drop(columns=['geoloc_id', 'OBJECTID_x', 'OBJECTID_y', 'longitude', 'latitude'])
    df = df.rename(columns={'data_name': 'Indicador', 'value': 'Valor', 'refdate': 'Ano'})
    df = df.dropna(subset=['Ano'])
    df['Ano'] = pd.to_datetime(df['Ano']).dt.year.astype(int)

# ---------- Filtros no sidebar ----------

st.sidebar.header("Filtros")

# Indicador (multiselect)
indicadores = df["Indicador"].dropna().unique()
indicador_sel = st.sidebar.multiselect("Selecione os indicadores", indicadores, default=indicadores[:1])

# Estado (selectbox)
estados = df["estado"].dropna().unique()
estado_sel = st.sidebar.selectbox("Selecione o estado", sorted(estados), index=0)

# Ano (selectbox)
anos = df["Ano"].dropna().unique()
ano_sel = st.sidebar.selectbox("Selecione o ano", sorted(anos, reverse=True), index=0)

# Botão para aplicar filtro
aplicar_filtro = st.sidebar.button("Aplicar filtro")

# --- Aplicar filtros ---
if aplicar_filtro:
    df_filtrado = df[
        (df["Indicador"].isin(indicador_sel)) &
        (df["estado"] == estado_sel) &
        (df["Ano"] == ano_sel)
    ]
    st.success("Filtro aplicado!")
else:
    # Aplica os filtros com os valores selecionados no sidebar mesmo sem clicar no botão
    df_filtrado = df[
        (df["Indicador"].isin(indicador_sel)) &
        (df["estado"] == estado_sel) &
        (df["Ano"] == ano_sel)
    ]

# --- Exibir PyGWalker ---
st.markdown("**Antes de criar um gráfico, defina no filtro o indicador, o estado e o ano.**")
st.markdown("Foram carregados dados apenas a Região Norte e ano de 2022 devido a limitação de processamento da versão gratuita do Streamlit Cloud")
st.subheader("Explore os dados abaixo 👇")

#pyg_app = StreamlitRenderer(df_filtrado)
#pyg_app.explorer()

walker = pyg.walk(df_filtrado)
