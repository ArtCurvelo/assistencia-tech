# Design: Publicação do site

## Decisions

### D1. Render com Docker

O Render publica direto do GitHub e tem plano gratuito para serviços web com WebSocket, de que o Reflex precisa. A imagem Docker deixa o ambiente igual ao testado: Python 3.14 (o da `.venv` e do CI), Node.js e as dependências de `requirements.txt`.

### D2. Uma porta só, sem compilar ao iniciar

O Render expõe uma única porta (`PORT`) e o plano gratuito tem 512 MB. A primeira versão iniciava com `reflex run --env prod --single-port`, que recompila o frontend ao subir e estourou a memória ("Ran out of memory (used over 512MB)"). A imagem agora inicia só o servidor Granian (`python -m granian --interface asgi --factory assistencia_tech.assistencia_tech:app`) com as variáveis internas do Reflex `__REFLEX_SKIP_COMPILE=true` e `__REFLEX_MOUNT_FRONTEND_COMPILED_APP=true`, o mesmo que o `--single-port` faz por dentro, mas sem a compilação: o processo usa cerca de 120 MB. Sem Redis, há um processo, e as sessões (com o token do Xano guardado no servidor) ficam na memória dele: reiniciar ou dormir o serviço encerra as sessões, e o usuário entra de novo.

### D3. Frontend compilado na construção

`reflex export --frontend-only --no-zip --env prod` roda durante a construção da imagem e gera `.web/build/client`. O endereço do backend gravado no frontend fica como `localhost`; o próprio frontend do Reflex (`getBackendURL`) troca, no navegador, `localhost` pelo domínio da página e usa `wss://` sem porta quando a página está em HTTPS. Assim a imagem não depende de saber o endereço público na construção.

### D4. Endereço público

O frontend precisa saber o endereço do backend (`api_url`). `rxconfig.py` usa `ASSISTENCIA_PUBLIC_URL`, se definida, ou `RENDER_EXTERNAL_URL`, que o Render define em todo serviço; sem nenhuma das duas (desenvolvimento), mantém os padrões do Reflex. `REFLEX_API_URL` continua tendo prioridade, como em qualquer configuração do Reflex.

### D5. Sem segredos

`render.yaml` define apenas `ASSISTENCIA_DATA_SOURCE=xano` e `XANO_BASE_URL` (endereço público da instância). Cada usuário entra com a própria conta do Xano; nenhuma credencial vai para o repositório ou para o painel do Render.

### D6. Telemetria desligada

`telemetry_enabled=False`: o Reflex não envia dados de uso do site publicado.

## Risks / Trade-offs

- [Site dormindo no plano gratuito] → o primeiro acesso após 15 minutos leva cerca de um minuto; avisado no README.
- [Limite do Xano gratuito com vários visitantes] → o cache de 15 segundos e o espaçamento de requisições da aplicação continuam valendo; o limite é do plano do Xano.
- [Imagem não testada localmente] → a construção é verificada pelo próprio Render; o modo produção numa porta é testado antes no computador.
