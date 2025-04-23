# Painel de Indicadores da Política Nacional de Desenvolvimento Regional (PNDR)

Este repositório contém o código-fonte do aplicativo **[Consulta ao Painel de Indicadores da PNDR](https://pindrtabulacao.streamlit.app/)**, desenvolvido como parte do **Sistema Nacional de Informações do Desenvolvimento Regional (SNIDR)**. O painel tem como objetivo facilitar o acesso, análise e visualização de indicadores regionais relevantes para a implementação e monitoramento da **Política Nacional de Desenvolvimento Regional**, conforme estabelecido pelo [Decreto nº 11.962, de 22 de março de 2024](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2024/decreto/d11962.htm).

## 🔍 Objetivo

Oferecer uma ferramenta interativa e acessível para explorar dados territoriais e socioeconômicos, com foco no desenvolvimento regional, a partir de uma interface gráfica baseada na web. A aplicação permite:

- Consulta e filtragem de indicadores por data, território e tema.
- Geração automatizada de gráficos e mapas interativos.
- Download de dados para análises externas.

## 🛠️ Tecnologias Utilizadas

- [Python](https://www.python.org/)
- [Streamlit](https://streamlit.io/) – Interface web interativa
- [Plotly](https://plotly.com/python/) / [Seaborn](https://seaborn.pydata.org/) / [Folium](https://python-visualization.github.io/folium/) – Visualizações
- [ArcGIS API for Python](https://developers.arcgis.com/python/) – Acesso a dados geográficos oficiais

## 🚀 Como Executar Localmente

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/painel-pndr.git
   cd painel-pndr
   
2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # No Windows: .venv\Scripts\activate
   pip install -r requirements.txt

4. Criar arquivo .env com as credenciais do ArcGIS API for Python

5. Execute o aplicativo:
   ```bash
   streamlit run app.py

## 📊 Fontes de Dados
Os dados utilizados neste painel são provenientes de fontes públicas e oficiais, como:
- Instituto Brasileiro de Geografia e Estatística (IBGE)
- Plataforma ArcGIS do Ministério da Integração e do Desenvolvimento Regional
- Outras bases integradas ao SNIDR

## 🏛️ Referência Legal
A Política Nacional de Desenvolvimento Regional (PNDR) tem como objetivo reduzir as desigualdades regionais e promover o desenvolvimento equilibrado do território brasileiro, conforme o Decreto nº 11.962/2024, que estabelece diretrizes para a governança da PNDR e a implementação do Sistema Nacional de Informações do Desenvolvimento Regional (SNIDR).
