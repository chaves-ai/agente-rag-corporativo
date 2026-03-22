FROM python:3.12-slim

WORKDIR /app

# Dependencias do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala torch versao CPU — sem NVIDIA — muito menor
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu

# Copia e instala o resto das dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o projeto
COPY . .

# Cria as pastas de dados
RUN mkdir -p data/raw data/processed data/vector_store

EXPOSE 8000

CMD ["uvicorn", "api.main_api:app", "--host", "0.0.0.0", "--port", "8000"]