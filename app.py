import streamlit as st
from config import conectar_portal
import pandas as pd
import pygwalker as pyg
from pygwalker.api.streamlit import StreamlitRenderer
import datetime

st.set_page_config(page_title="Painel de Indicadores", layout="wide")
st.title("Tabulação para o Painel de Indicadores")

# Função modificada para receber os indicadores desejados
@st.cache_data
def carregar_valores_df(inicio='2019-12-31', fim='2022-12-31', indicadores=None):
    gis = conectar_portal()
    valores_item = gis.content.search("valoresmeta", item_type="Map Image Layer")[0]
    valores_table = valores_item.tables[0]
    # Define o filtro básico de data
    query_where = f"refdate >= DATE '{inicio}' AND refdate <= DATE '{fim}'"
    # Se houver seleção de indicadores, adiciona o filtro na query
    if indicadores and len(indicadores) > 0:
        indicadores_str = ", ".join([f"'{ind}'" for ind in indicadores])
        query_where += f" AND data_name IN ({indicadores_str})"
    valores_set = valores_table.query(
        where=query_where,
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

# Carrega o arquivo Lista_indicadores.csv e extrai a lista de indicadores disponíveis
indicadores_lista = pd.read_csv("Lista_indicadores.csv", sep=";", encoding="latin1")
lista_indicadores = indicadores_lista['data_name'].dropna().unique().tolist()

# --- Filtros no Sidebar ---
st.sidebar.header("Filtros")

# Define o indicador padrão
indicador_padrao = 'Percentual de escolas com acesso a esgotamento sanitário'
if indicador_padrao in lista_indicadores:
    default_indicadores = [indicador_padrao]
else:
    default_indicadores = [lista_indicadores[0]] if lista_indicadores else []

# Seletor de indicadores baseado no CSV
indicador_sel = st.sidebar.multiselect("Selecione os indicadores", lista_indicadores, default=default_indicadores)

# Filtro de datas (intervalo de anos será definido após a junção dos dados)
with st.spinner("Carregando dados, esse processo pode levar alguns minutos..."):
    # Passa os indicadores selecionados para a função de carregamento
    valores_df = carregar_valores_df(indicadores=indicador_sel)
    recortes_df = carregar_recortes_df()
    df = valores_df.merge(recortes_df, left_on='geoloc_id', right_on='codigo_ibge', how='left')
    df = df.drop(columns=['geoloc_id', 'OBJECTID_x', 'OBJECTID_y', 'longitude', 'latitude'])
    df = df.rename(columns={'data_name': 'Indicador', 'value': 'Valor', 'refdate': 'Ano'})
    df = df.dropna(subset=['Ano'])
    df['Ano'] = pd.to_datetime(df['Ano']).dt.year.astype(int)

# --- Filtros adicionais (datas) ---
anos_disponiveis = sorted(df["Ano"].dropna().unique())
ano_min, ano_max = int(min(anos_disponiveis)), int(max(anos_disponiveis))
valor_padrao = (2020, 2022) if 2020 in anos_disponiveis and 2022 in anos_disponiveis else (ano_min, ano_max)

periodo = st.sidebar.select_slider(
    "Selecione o intervalo de anos",
    options=anos_disponiveis,
    value=valor_padrao
)

# Aplica o filtro de datas ao DataFrame
df_filtrado = df[df["Ano"].between(periodo[0], periodo[1])]

# --- Exibir PyGWalker ---
st.subheader("Explore os dados abaixo 👇")
#vis_spec = r"""{"config":[{"config":{"defaultAggregated":true,"geoms":["bar"],"coordSystem":"generic","limit":-1,"timezoneDisplayOffset":0},"encodings":{"dimensions":[{"fid":"Indicador","name":"Indicador","basename":"Indicador","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"Ano","name":"Ano","basename":"Ano","semanticType":"quantitative","analyticType":"dimension","offset":0},{"fid":"município","name":"município","basename":"município","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"estado","name":"estado","basename":"estado","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"região","name":"região","basename":"região","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"faixa_de_fronteira","name":"faixa_de_fronteira","basename":"faixa_de_fronteira","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"participacao_semiarido","name":"participacao_semiarido","basename":"participacao_semiarido","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"regiao_intermediaria","name":"regiao_intermediaria","basename":"regiao_intermediaria","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"tipologia","name":"tipologia","basename":"tipologia","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"participacao_sudene","name":"participacao_sudene","basename":"participacao_sudene","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"regiao_imediata","name":"regiao_imediata","basename":"regiao_imediata","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"participacao_amazonia_legal","name":"participacao_amazonia_legal","basename":"participacao_amazonia_legal","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"gw_mea_key_fid","name":"Measure names","analyticType":"dimension","semanticType":"nominal"}],"measures":[{"fid":"Valor","name":"Valor","basename":"Valor","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"codigo_ibge","name":"codigo_ibge","basename":"codigo_ibge","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"gw_count_fid","name":"Row count","analyticType":"measure","semanticType":"quantitative","aggName":"sum","computed":true,"expression":{"op":"one","params":[],"as":"gw_count_fid"}},{"fid":"gw_mea_val_fid","name":"Measure values","analyticType":"measure","semanticType":"quantitative","aggName":"sum"}],"rows":[{"fid":"município","name":"município","basename":"município","semanticType":"nominal","analyticType":"dimension","offset":0}],"columns":[{"fid":"Valor","name":"Valor","basename":"Valor","analyticType":"measure","semanticType":"quantitative","aggName":"mean","offset":0}],"color":[{"fid":"tipologia","name":"tipologia","basename":"tipologia","semanticType":"nominal","analyticType":"dimension","offset":0}],"opacity":[],"size":[],"shape":[],"radius":[],"theta":[],"longitude":[],"latitude":[],"geoId":[],"details":[],"filters":[{"fid":"Indicador","name":"Indicador","basename":"Indicador","semanticType":"nominal","analyticType":"dimension","offset":0,"rule":{"type":"one of","value":[" Percentual de escolas com acesso a esgotamento sanitário"]}},{"fid":"estado","name":"estado","basename":"estado","semanticType":"nominal","analyticType":"dimension","offset":0,"rule":{"type":"one of","value":["Rondônia"]}},{"fid":"Ano","name":"Ano","basename":"Ano","semanticType":"quantitative","analyticType":"dimension","offset":0,"rule":{"type":"not in","value":[2021,2019]}}],"text":[]},"layout":{"showActions":false,"showTableSummary":false,"stack":"stack","interactiveScale":false,"zeroScale":true,"size":{"mode":"auto","width":320,"height":200},"format":{},"geoKey":"name","resolve":{"x":false,"y":false,"color":false,"opacity":false,"shape":false,"size":false}},"visId":"gw_H9hc","name":"Chart 1"}],"chart_map":{},"workflow_list":[{"workflow":[{"type":"filter","filters":[{"fid":"Indicador","rule":{"type":"one of","value":[" Percentual de escolas com acesso a esgotamento sanitário"]}},{"fid":"estado","rule":{"type":"one of","value":["Rondônia"]}},{"fid":"Ano","rule":{"type":"not in","value":[2021,2019]}}]},{"type":"view","query":[{"op":"aggregate","groupBy":["município","tipologia"],"measures":[{"field":"Valor","agg":"mean","asFieldKey":"Valor_mean"}]}]}]}],"version":"0.4.9.15"}"""
pyg_app = StreamlitRenderer(df_filtrado)
pyg_app.explorer()