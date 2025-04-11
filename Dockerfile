# Usa a imagem base oficial do Streamlit
FROM streamlit/streamlit:latest

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    libkrb5-dev \  # Para o pacote gssapi
    build-essential \  # Ferramentas de compilação
    libssl-dev \  # Dependências criptográficas
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos do seu aplicativo
COPY . /app
WORKDIR /app

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Configura a porta do Streamlit
EXPOSE 8501

# Comando para executar o app
CMD ["streamlit", "run", "app.py", "--server.port=8501"]