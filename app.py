import streamlit as st
from config import conectar_portal
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static
import requests

st.set_page_config(page_title="Painel de Indicadores", layout="wide")
st.title("\U0001F4CA Painel de Indicadores Municipais")

#######################
# Carregar dados do IBGE
@st.cache_data
def get_br_municipio():
    url = "https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo+json&qualidade=maxima&intrarregiao=municipio"
    return requests.get(url).json()

# Uso da função
geojson_data = get_br_municipio()

def create_map(df_filtrado, geojson_data, municipio_destacado=None):
    """Cria mapas com Folium e adiciona marcador se um município for destacado."""
    if {'latitude', 'longitude'}.issubset(df_filtrado.columns):
        st.write(f"### \U0001F4C8 {indicador_sel} - {estado_sel} ({ano_sel}) - municípios")
        m = folium.Map(location=[df_filtrado['latitude'].mean(), df_filtrado['longitude'].mean()], zoom_start=5)
        folium.Choropleth(
            geo_data=geojson_data, 
            name="Indicador",
            data=df_filtrado,
            columns=["codarea", "Valor"],
            legend_name="Indicador",
            key_on="feature.properties.codarea",
            nan_fill_color="white",
            nan_fill_opacity=0.4,
            fill_color="OrRd",
            fill_opacity=0.8,
            line_weight=0.1,
        ).add_to(m)

        # Adiciona marcador para o município selecionado
        if municipio_destacado:
            mun_df = df_filtrado[df_filtrado["município"] == municipio_destacado]
            if not mun_df.empty:
                lat = mun_df.iloc[0]["latitude"]
                lon = mun_df.iloc[0]["longitude"]
                valor = mun_df.iloc[0]["Valor"]
                folium.Marker(
                    location=[lat, lon],
                    tooltip=f"{municipio_destacado} = {valor:.2f}",
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(m)

        folium.LayerControl().add_to(m)
        folium_static(m)

###############

# Código para carregar dados via API ArcGIS

@st.cache_data
# Limitado a Região Norte e anos de 2021 a 2022
def carregar_valores_df(inicio='2021-01-01', fim='2022-12-31'):
    return pd.DataFrame([
        f.attributes
        for f in conectar_portal()
            .content
            .search("valoresmeta", item_type="Map Image Layer")[0]
            .tables[0]
            .query(
                where=f"refdate >= DATE '{inicio}' AND refdate <= DATE '{fim}'",
                out_fields="geoloc_id, data_name, value, refdate"
            ).features
    ])

@st.cache_data
def carregar_recortes_df():
    return pd.DataFrame([
        f.attributes
        for f in conectar_portal()
            .content
            .search("recortes_geograficos", item_type="Map Image Layer")[0]
            .layers[0]
            .query(
                where="1=1",
                out_fields="*"
            ).features
    ])

with st.spinner("Carregando dados, esse processo pode levar alguns minutos..."):
    # Carrega e trata os dados
    valores_df = carregar_valores_df().drop_duplicates(subset=['geoloc_id', 'data_name', 'value', 'refdate'], keep='first').reset_index(drop=True)
    recortes_df = carregar_recortes_df()
    
    # Faz o merge e mantém apenas o necessário desde o início
    df = valores_df.merge(
        recortes_df,
        left_on="geoloc_id",
        right_on="codigo_ibge",
        how="left"
    ).dropna(subset=["codigo_ibge"])

    # Mantêm apenas as colunas relevantes
    df = df.drop(columns=['geoloc_id', 'OBJECTID_x', 'OBJECTID_y'])

    # Renomeia e converte colunas
    df = df.rename(columns={
        "codigo_ibge": "codarea",
        "data_name": "Indicador",
        "value": "Valor",
        "refdate": "Ano"
    })
    df['Ano'] = pd.to_datetime(df['Ano']).dt.year.astype(int)

# ---------- Filtros no sidebar ----------

st.sidebar.header("\U0001F50D Filtros")

# Indicador (selectbox)
indicadores = df["Indicador"].dropna().unique()
indicador_sel = st.sidebar.selectbox("Selecione os indicadores", indicadores, index=0)

# Estado (selectbox)
estados = df["estado"].dropna().unique()
estado_sel = st.sidebar.selectbox("Selecione o estado", sorted(estados), index=0)

# Ano (selectbox)
anos = df["Ano"].dropna().unique()
ano_sel = st.sidebar.selectbox("Selecione o ano", sorted(anos, reverse=True), index=0)

# --- Aplicar filtros ---
df_filtrado = df[
    (df["Indicador"] == indicador_sel) &
    (df["estado"] == estado_sel) &
    (df["Ano"] == ano_sel)
]

# --- Exibir ---
st.markdown("""
> _Foram carregados dados apenas para os anos de 2021 e 2022 devido a limitações do servidor._
""")

if df_filtrado.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

############### Colunas para exibir dados ###############
col = st.columns((4, 4), gap='medium')


############### Coluna da esquerda: Resumo estatístico
with col[0]:
    # Novo filtro dependente: seleção de município
    municipios = df_filtrado["município"].dropna().unique()
    municipio_sel = st.selectbox("\U0001F50D Selecione o município para análise comparativa", sorted(municipios))

    # Filtra o município escolhido
    df_municipio = df_filtrado[df_filtrado["município"] == municipio_sel]

    if not df_municipio.empty:
        reg_imediata = df_municipio["regiao_imediata"].values[0]
        reg_intermediaria = df_municipio["regiao_intermediaria"].values[0]

        df_estado = df_filtrado  # já está filtrado por estado
        df_ri = df_filtrado[df_filtrado["regiao_imediata"] == reg_imediata]
        df_rint = df_filtrado[df_filtrado["regiao_intermediaria"] == reg_intermediaria]

        # Constrói DataFrame para o gráfico
        df_scatter = pd.concat([
            df_estado.assign(Grupo="Estado"),
            df_rint.assign(Grupo="Região Intermediária"),
            df_ri.assign(Grupo="Região Imediata"),
            df_municipio.assign(Grupo="Município Selecionado")
        ])

        df_scatter["Grupo"] = pd.Categorical(df_scatter["Grupo"], categories=[
            "Município Selecionado", "Região Imediata", "Região Intermediária", "Estado"
        ][::-1])  # ordem invertida para eixo y

        # Calcula médias por grupo
        medias = df_scatter.groupby("Grupo")["Valor"].mean().reset_index()
        medias["município"] = "Média"

        # Gráfico de pontos
        fig = px.strip(
            df_scatter,
            x="Valor",
            y="Grupo",
            hover_name="município",
            color="Grupo",
            title=f"Comparação de {indicador_sel} ({ano_sel}) - {municipio_sel}",
            stripmode='overlay'
        )

        # Adiciona pontos de média
        for _, row in medias.iterrows():
            fig.add_scatter(
                x=[row["Valor"]],
                y=[row["Grupo"]],
                mode="markers+text",
                marker=dict(symbol='x', size=12, color='black'),
                text=["Média"],
                textposition="top right",
                showlegend=False
            )

        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Resumo estatístico
    st.subheader(f"📊 Resumo estatístico - {estado_sel}")
    resumo = df_filtrado["Valor"].describe().rename({
        "count": "Quantidade de municípios",
        "mean": "Valor médio do indicador",
        "std": "Desvio Padrão",
        "min": "Mínimo",
        "25%": "Percentil 25%",
        "50%": "Mediana",
        "75%": "Percentil 75%",
        "max": "Máximo"
    }).to_frame().reset_index()

    resumo.columns = ["Estatística", "Valor"]  # renomear as colunas depois do reset_index

    # Formatação de valores numéricos
    resumo["Valor"] = resumo["Valor"].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # Exibir com largura personalizada da coluna de estatísticas
    st.dataframe(
        resumo.style.set_properties(subset=["Estatística"], **{"width": "200px"}),
        height=320,
        use_container_width=True
    )

############### Coluna da direita: Mapa
with col[1]:
    create_map(df_filtrado, geojson_data, municipio_sel)


################## Abaixo das colunas
# Visualizações gráficas
st.subheader("\U0001F4C8 Visualização gráfica")

opcao_grafico = st.radio(
    "Escolha o tipo de gráfico:",
    ["Barras (Top N municípios)", "Boxplot (distribuição)", "Histograma (frequência)"],
    index=0,
    horizontal=True
)

if opcao_grafico == "Barras (Top N municípios)":
    limite = st.slider(
        "Quantos municípios exibir no gráfico?",
        min_value=5,
        max_value=min(100, len(df_filtrado)),
        value=20
    )

    df_plot = df_filtrado.sort_values(by="Valor", ascending=False).head(limite)

    fig = px.bar(
        df_plot,
        x="município",
        y="Valor",
        text="Valor",
        title=f"{indicador_sel} - {estado_sel} ({ano_sel}) - Top {limite} municípios",
        labels={"município": "Município", "Valor": "Valor"},
    )
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, height=500)
    st.plotly_chart(fig, use_container_width=True)

elif opcao_grafico == "Boxplot (distribuição)":
    fig = px.box(
        df_filtrado,
        y="Valor",
        points="all",
        title=f"Distribuição dos valores - {indicador_sel} ({estado_sel}, {ano_sel})",
        labels={"Valor": "Valor do Indicador"}
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

elif opcao_grafico == "Histograma (frequência)":
    fig = px.histogram(
        df_filtrado,
        x="Valor",
        nbins=30,
        title=f"Frequência dos valores - {indicador_sel} ({estado_sel}, {ano_sel})",
        labels={"Valor": "Valor do Indicador"},
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

# --- Exibir DataFrame completo ao final ---
st.subheader("📄 Tabela com os dados filtrados")
st.dataframe(df_filtrado, use_container_width=True, height=400)

st.download_button(
    label="📥 Baixar dados filtrados (.csv)",
    data=df_filtrado.to_csv(index=False).encode("utf-8"),
    file_name="dados_filtrados.csv",
    mime="text/csv"
)

