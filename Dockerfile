FROM python:3.10-slim

# diretório de trabalho
WORKDIR /app

# copia os arquivos
COPY . .

# instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# porta que o app usa
EXPOSE 8000

# comando para subir aplicação

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "--timeout", "120"]
