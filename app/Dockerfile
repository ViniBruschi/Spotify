# Usar uma imagem base do Python
FROM python:3.9-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar o requirements.txt para o diretório de trabalho
COPY req.txt .

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r req.txt

# Copiar o restante do código da aplicação para o diretório de trabalho
COPY . .

# Definir o comando padrão a ser executado quando o container iniciar
CMD ["python", "app.py"]
