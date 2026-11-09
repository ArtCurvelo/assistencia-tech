# Tasks

## 1. Configuração

- [x] 1.1 `rxconfig.py` com endereço público por `ASSISTENCIA_PUBLIC_URL`/`RENDER_EXTERNAL_URL` e telemetria desligada; verificar com teste.
- [x] 1.2 `Dockerfile`, `.dockerignore` e `render.yaml`, sem credenciais.

## 2. Verificação local

- [x] 2.1 Rodar o modo produção numa porta só (`--env prod --single-port`) com o Xano e conferir login, páginas e QR code no navegador.

## 3. Publicação

- [ ] 3.1 Com a confirmação do aluno, enviar ao GitHub e criar o serviço no Render pela conta dele; conferir o site publicado (página inicial, login, consulta pública e QR code) e registrar o endereço no README.

## Registro de verificação

- **pytest (.venv):** 438 passed (4 testes novos em `tests/test_deployment_config.py`).
- **Modo produção local** (`reflex run --env prod --single-port --frontend-port 8080`, fonte `xano`, `ASSISTENCIA_PUBLIC_URL=http://localhost:8080`):
  - `/ping`, `/` e `/style.css` → 200; `.web/env.json` com `ws://localhost:8080/_event` (endereço público aplicado);
  - `/consulta/OS-2026-00002` → página com a ordem real do Xano ("Em reparo", "Notebook Inspiron 15");
  - `/login` sem o acesso rápido da demonstração.
- **Limitação conhecida (Reflex 0.8.28):** rotas dinâmicas (`/consulta/<código>`, `/admin/ordens/<código>`) não são pré-geradas; o servidor entrega a página com HTTP 404 e o navegador monta a página correta. Funciona no navegador e no celular.
- **Imagem Docker:** não construída localmente; a construção é verificada pelo Render.
