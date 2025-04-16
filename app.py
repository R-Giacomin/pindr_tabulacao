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

@st.cache_data
def carregar_dados():
    # Download the duckdb file
    url = "https://raw.githubusercontent.com/R-Giacomin/Painel_PNDR/main/data/dados_reduzido.db"
    file_path = "dados_reduzido.db"

    if not os.path.exists(file_path):
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes

        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

    # Connect to the database
    con = duckdb.connect(database=file_path, read_only=True)

    # Execute the query and fetch the results into a pandas DataFrame
    query1 = "SELECT * FROM recortes_geograficos"
    query2 = "SELECT * FROM valoresmeta"
    recortes_geograficos = con.execute(query1).fetchdf()
    valoresmeta = con.execute(query2).fetchdf()

    # Close the connection
    con.close()

    df = valoresmeta.merge(recortes_geograficos, left_on='geoloc_id', right_on='codigo_ibge', how='left')
    df = df.dropna(subset=['codigo_ibge'])
    df = df.drop(columns=['mdata_id',	'geoloc_id',	'local_id', 'geoloc_id', 'local_name'])
    df = df.rename(columns={'data_name': 'Indicador','orig_name': 'Sigla_indicador' ,'value': 'Valor', 'refdate': 'Ano'})
    df = df.dropna(subset=['Ano'])
    df['Ano'] = pd.to_datetime(df['Ano']).dt.year.astype(int)
    return df

with st.spinner("Carregando dados, esse processo pode levar alguns minutos..."):
    df = carregar_dados()

#@st.cache_data
#def carregar_valores_df(inicio='2020-12-31', fim='2022-12-31'):
#    gis = conectar_portal()
#    valores_item = gis.content.search("valoresmeta", item_type="Map Image Layer")[0]
#    valores_table = valores_item.tables[0]
#    valores_set = valores_table.query(
#        where=f"refdate >= DATE '{inicio}' AND refdate <= DATE '{fim}'",
#        out_fields="geoloc_id, data_name, value, refdate"
#    )
#    return pd.DataFrame([f.attributes for f in valores_set.features])

#@st.cache_data
#def carregar_recortes_df():
#    gis = conectar_portal()
#    recortes_item = gis.content.search("recortes_geograficos", item_type="Map Image Layer")[0]
#    recortes_layer = recortes_item.layers[0]
#    valores_set = recortes_layer.query(where="1=1", out_fields="*")
#    return pd.DataFrame([f.attributes for f in valores_set.features])

#with st.spinner("Carregando dados, esse processo pode levar alguns minutos..."):
#    valores_df = carregar_valores_df()
#    recortes_df = carregar_recortes_df()
#    df = valores_df.merge(recortes_df, left_on='geoloc_id', right_on='codigo_ibge', how='outer')
#    df = df.dropna(subset=['codigo_ibge'])
#    df = df.drop(columns=['geoloc_id', 'OBJECTID_x', 'OBJECTID_y', 'longitude', 'latitude'])
#    df = df.rename(columns={'data_name': 'Indicador', 'value': 'Valor', 'refdate': 'Ano'})
#    df = df.dropna(subset=['Ano'])
#    df['Ano'] = pd.to_datetime(df['Ano']).dt.year.astype(int)

# --- Filtros ---
st.sidebar.header("Filtros")

# Indicadores
indicadores = df["Indicador"].dropna().unique()
indicador_sel = st.sidebar.multiselect("Selecione os indicadores", indicadores, default=indicadores[:1])

df_filtrado = df[
    (df["Indicador"].isin(indicador_sel))
]

# --- Exibir PyGWalker ---
st.subheader("Explore os dados abaixo 👇")

pyg_app = StreamlitRenderer(df_filtrado)
pyg_app.explorer()