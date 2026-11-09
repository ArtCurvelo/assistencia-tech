# Tasks

## 1. Configuração

- [x] 1.1 `rxconfig.py` com endereço público por `ASSISTENCIA_PUBLIC_URL`/`RENDER_EXTERNAL_URL` e telemetria desligada; verificar com teste.
- [x] 1.2 `Dockerfile`, `.dockerignore` e `render.yaml`, sem credenciais.

## 2. Verificação local

- [x] 2.1 Rodar o modo produção numa porta só (`--env prod --single-port`) com o Xano e conferir login, páginas e consulta no navegador (o QR code foi conferido no site publicado).

## 3. Publicação

- [x] 3.1 Com a confirmação do aluno, enviar ao GitHub e criar o serviço no Render pela conta dele; conferir o site publicado (página inicial, login, consulta pública e QR code) e registrar o endereço no README.

## Registro de verificação

- **pytest (.venv):** 438 passed (4 testes novos em `tests/test_deployment_config.py`).
- **Modo produção local** (`reflex run --env prod --single-port --frontend-port 8080`, fonte `xano`, `ASSISTENCIA_PUBLIC_URL=http://localhost:8080`):
  - `/ping`, `/` e `/style.css` → 200; `.web/env.json` com `ws://localhost:8080/_event` (endereço público aplicado);
  - `/consulta/OS-2026-00002` → página com a ordem real do Xano ("Em reparo", "Notebook Inspiron 15");
  - `/login` sem o acesso rápido da demonstração.
- **Limitação conhecida (Reflex 0.8.28):** rotas dinâmicas (`/consulta/<código>`, `/admin/ordens/<código>`) não são pré-geradas; o servidor entrega a página com HTTP 404 e o navegador monta a página correta. Funciona no navegador e no celular.
- **Primeiro deploy no Render (`470e765`):** a imagem foi construída, mas o serviço caiu com "Ran out of memory (used over 512MB)": `reflex run --env prod --single-port` recompila o frontend ao iniciar.
- **Correção (`a838b16`):** frontend compilado na construção (`reflex export --frontend-only --no-zip --env prod`) e início só do Granian com `__REFLEX_SKIP_COMPILE` e `__REFLEX_MOUNT_FRONTEND_COMPILED_APP`; testado localmente antes (cerca de 120 MB, consulta da OS-2026-00001 com dados do Xano pelo WebSocket).
- **Site publicado** (`https://assistencia-tech-2eyb.onrender.com`, deploy de `a838b16`): `/ping` 200 cerca de 60 s após o envio; `/` e `/style.css` 200; `/consulta/OS-2026-00001` no navegador → "Entregue", "Notebook Inspiron 15", com a conexão `wss://` no HTTPS do Render.
- **Login e QR code no site publicado:** com a sessão de administrador do aluno, `/admin/ordens/OS-2026-00001/comprovante` abriu o "Comprovante de entrega"; o texto traz `https://assistencia-tech-2eyb.onrender.com/consulta/OS-2026-00001`, e a imagem do QR code é idêntica (mesmo tamanho e hash) à gerada pelo `segno` para esse endereço.
