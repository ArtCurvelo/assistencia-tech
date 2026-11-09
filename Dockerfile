# Imagem de produção do Assistência TECH (mudança add-public-deployment).
# O frontend é compilado na construção; ao iniciar, só o servidor Granian sobe e
# serve o frontend pronto e o backend numa única porta ($PORT). Recompilar ao
# iniciar estourava os 512 MB do plano gratuito do Render.
FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    REFLEX_TELEMETRY_ENABLED=false \
    REFLEX_ENV_MODE=prod \
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

# Compila o frontend de produção em .web/build/client. O endereço do backend fica
# como localhost, e o próprio frontend do Reflex o troca, no navegador, pelo
# domínio da página (wss:// e sem porta em HTTPS).
RUN reflex export --frontend-only --no-zip --env prod

# Variáveis internas do Reflex (nomes com "__"): não recompilar ao iniciar e
# montar o frontend compilado no backend, como faz "reflex run --single-port".
ENV __REFLEX_SKIP_COMPILE=true \
    __REFLEX_MOUNT_FRONTEND_COMPILED_APP=true

EXPOSE 8080

CMD ["sh", "-c", "exec python -m granian --host 0.0.0.0 --port \"$PORT\" --interface asgi --factory assistencia_tech.assistencia_tech:app"]
