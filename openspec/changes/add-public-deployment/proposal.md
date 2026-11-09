# Proposal: Publicação do site

## Why

O sistema só roda no computador do aluno. Para a avaliação, o professor precisa abrir o site de qualquer lugar e usar o sistema completo com o backend real, sem instalar Python, Node ou Reflex. O comprovante também depende disso: o QR code só funciona no celular do cliente se apontar para um endereço público.

## What Changes

- **Imagem Docker** (`Dockerfile` e `.dockerignore`) que instala as dependências, prepara o frontend do Reflex durante a construção e roda o aplicativo em modo produção numa única porta (`reflex run --env prod --single-port`), na porta definida pela hospedagem.
- **Render** (`render.yaml`): serviço web gratuito construído a partir do repositório no GitHub, com a fonte de dados `xano` e o endereço da instância; a cada envio ao `main`, o site é atualizado.
- **Endereço público automático:** `rxconfig.py` usa `ASSISTENCIA_PUBLIC_URL` ou, no Render, `RENDER_EXTERNAL_URL` como endereço da API e do site; o QR code dos comprovantes passa a apontar para o domínio público.
- **Telemetria do Reflex desligada** (`telemetry_enabled=False`).
- **README:** endereço do site publicado e como publicar de novo.

## Capabilities

### New Capabilities

- `public-deployment`: publicação do sistema num endereço público com o backend real.

### Modified Capabilities

- Nenhuma.

## Impact

- **Arquivos:** `Dockerfile`, `.dockerignore`, `render.yaml`, `rxconfig.py`, README.
- **Conta:** o Render exige uma conta do aluno ligada ao GitHub; nenhuma credencial entra no repositório (o acesso ao Xano usa o token de cada usuário).
- **Limites:** no plano gratuito, o site dorme após 15 minutos sem acesso; o Xano gratuito aceita 10 requisições a cada 20 segundos.

## Out of Scope

- Domínio próprio.
- Redis e mais de um processo (as sessões ficam na memória do único processo).
- Publicação automática condicionada ao CI.
