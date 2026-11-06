# Tasks

## 1. Inspeção e preparação

- [ ] 1.1 Inspecionar a estrutura do projeto Reflex, identificar páginas, componentes, estilos e dependências; verificar a conclusão registrando o inventário dos arquivos relevantes.
- [ ] 1.2 Mapear as rotas existentes (`/`, `/servicos`, `/login`, `/cadastro`, `/admin`, `/admin/clientes`, `/admin/equipamentos` e `/admin/ordens`) e conferir seu comportamento no ambiente de desenvolvimento.
- [ ] 1.3 Identificar os fluxos funcionais de autenticação, formulários, navegação e administração; verificar a conclusão registrando os comportamentos que precisam ser preservados.
- [ ] 1.4 Identificar os mecanismos de integração existentes e documentar seus pontos de uso sem presumir contratos ou endpoints futuros do Xano.

## 2. Sistema visual e componentes compartilhados

- [ ] 2.1 Definir os tokens visuais de cores, tipografia, espaçamento, bordas, sombras e foco; verificar a conclusão conferindo sua aplicação consistente em uma página de referência.
- [ ] 2.2 Implementar ou adaptar os componentes compartilhados de botões, campos, cartões e navegação; verificar a conclusão confirmando que preservam suas funções e apresentam estilos consistentes.
- [ ] 2.3 Padronizar mensagens de erro, sucesso, carregamento e ausência de dados; verificar a conclusão observando cada estado nas funcionalidades em que se aplica.
- [ ] 2.4 Verificar os estados de foco e interação dos componentes compartilhados e corrigir problemas de legibilidade ou identificação dos controles.

## 3. Páginas públicas e autenticação

- [ ] 3.1 Redesenhar a página inicial (`/`) com hierarquia visual clara e chamadas para ação; verificar a conclusão conferindo navegação e funcionamento dos links existentes.
- [ ] 3.2 Redesenhar a página de serviços (`/servicos`) para organizar e apresentar as opções disponíveis; verificar a conclusão conferindo o conteúdo e as ações existentes.
- [ ] 3.3 Redesenhar a página de login (`/login`) sem alterar a lógica de autenticação; verificar a conclusão testando a apresentação de validações e os fluxos existentes.
- [ ] 3.4 Redesenhar a página de cadastro (`/cadastro`) sem alterar as regras de negócio; verificar a conclusão conferindo os campos, as validações e o comportamento de envio existentes.
- [ ] 3.5 Verificar as páginas públicas e de autenticação em execução, corrigindo regressões visuais ou funcionais antes de prosseguir.

## 4. Área administrativa

- [ ] 4.1 Redesenhar o painel administrativo (`/admin`) com hierarquia visual e navegação claras; verificar a conclusão conferindo os acessos e os comportamentos já existentes.
- [ ] 4.2 Redesenhar a página de clientes (`/admin/clientes`) mantendo os dados e as ações existentes; verificar a conclusão conferindo listagem, estados vazios e operações disponíveis.
- [ ] 4.3 Redesenhar a página de equipamentos (`/admin/equipamentos`) mantendo os dados e as ações existentes; verificar a conclusão conferindo a apresentação dos registros e os fluxos disponíveis.
- [ ] 4.4 Redesenhar a página de ordens de serviço (`/admin/ordens`) organizando as informações e os estados das ordens; verificar a conclusão conferindo os dados e as ações existentes.
- [ ] 4.5 Validar cada página administrativa após as alterações e corrigir regressões antes de avançar.

## 5. Responsividade e acessibilidade

- [ ] 5.1 Inspecionar os layouts implementados e identificar os pontos de adaptação necessários para celular, tablet e computador; registrar as larguras de referência adequadas aos componentes reais.
- [ ] 5.2 Adaptar navegação, menus e ações para telas pequenas; verificar a conclusão confirmando que os controles permanecem acessíveis e utilizáveis.
- [ ] 5.3 Adaptar formulários, campos, rótulos e mensagens de validação para diferentes larguras; verificar a conclusão preenchendo e enviando os formulários nos tamanhos de tela definidos.
- [ ] 5.4 Adaptar tabelas, listas e cartões administrativos para telas menores; verificar a conclusão confirmando que informações e ações essenciais continuam acessíveis sem rolagem horizontal da página inteira.
- [ ] 5.5 Conferir legibilidade, foco, identificação dos controles e ausência de sobreposições nas páginas em celular, tablet e computador; corrigir os problemas encontrados.

## 6. Compatibilidade e preservação funcional

- [ ] 6.1 Conferir que todas as rotas existentes continuam acessíveis conforme as regras atuais de navegação e autorização; verificar a conclusão testando cada rota.
- [ ] 6.2 Conferir que as alterações visuais preservam a lógica dos formulários, os estados da aplicação e as operações existentes; verificar a conclusão executando os fluxos funcionais identificados na inspeção.
- [ ] 6.3 Conferir que os mecanismos de integração existentes continuam compatíveis e que nenhum contrato de API foi inventado ou alterado sem documentação; verificar a conclusão revisando os pontos de integração afetados.
- [x] 6.4 Executar os testes automatizados disponíveis e corrigir falhas introduzidas pelo redesign; verificar a conclusão registrando o resultado dos testes.

## 7. Revisão integrada

- [ ] 7.1 Executar a aplicação e revisar todas as páginas contempladas, confirmando consistência visual, navegação e funcionamento dos componentes compartilhados.
- [ ] 7.2 Repetir a validação responsiva em celular, tablet e computador e corrigir problemas encontrados na integração entre páginas.
- [x] 7.3 Executar `openspec validate redesign-interface` e confirmar que a mudança continua válida.
- [x] 7.4 Registrar as verificações realizadas, os problemas conhecidos e eventuais limitações que dependam da futura documentação do Xano.

## Workflow follow-up

- Após concluir as tarefas e revisar a implementação, arquivar a mudança com o fluxo oficial do OpenSpec.
- Após o arquivamento, verificar se as especificações principais foram atualizadas corretamente.

## Registro de validação

- CSS aplicado e carregado corretamente após o ajuste de `stylesheets=["/style.css"]` na configuração do Reflex; funcionamento visual confirmado pelo usuário.
- Testes automatizados: 3 passaram, 0 falharam.
- OpenSpec: `openspec validate redesign-interface` executado com sucesso.
- Ainda não foi realizada uma revisão completa de todas as rotas, fluxos funcionais e tamanhos de tela.
- Integrações com Xano permanecem dependentes da documentação oficial das APIs.