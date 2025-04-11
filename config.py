from arcgis.gis import GIS
import os
from dotenv import load_dotenv

#######################
# Carregar credenciais
# Load the environment variables
load_dotenv()

# Access the environment variable
usuario = os.environ.get('GEOINTEGRA_username')
senha = os.environ.get('GEOINTEGRA_password')
url = os.environ.get('GEOINTEGRA_url')

def conectar_portal():
    return GIS(url, usuario, senha)
