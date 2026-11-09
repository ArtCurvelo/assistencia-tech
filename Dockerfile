# Imagem de produção do Assistência TECH (mudança add-public-deployment).
# Um processo serve o frontend compilado e o backend numa única porta ($PORT).
FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    REFLEX_TELEMETRY_ENABLED=false \
    PORT=8080

# Node.js (>= 20.19, exigido pelo Reflex 0.8) e ferramentas para instalar o Bun.
RUN apt-get update \
    && apt-get install -y --no-install-recommends nodejs curl unzip ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && node --version

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Baixa o Bun e instala os pacotes do frontend durante a construção; ao iniciar,
# o modo produção só recompila o aplicativo com o endereço público.
RUN reflex export --frontend-only --no-zip

EXPOSE 8080

CMD ["sh", "-c", "exec reflex run --env prod --single-port --frontend-port \"$PORT\" --backend-host 0.0.0.0"]
