# Design

## Context

O Assistência TECH utiliza Python com Reflex para construir sua interface web. O projeto possui páginas públicas, páginas de autenticação e uma área administrativa, incluindo clientes, equipamentos e ordens de serviço.

A mudança deve preservar as rotas e a lógica existentes. A estrutura atual do frontend, os componentes disponíveis e os estilos efetivamente utilizados deverão ser inspecionados antes da implementação. Os contratos de integração com o Xano ainda não foram fornecidos e não devem ser presumidos.

Os requisitos de comportamento estão definidos em `specs/design-system/spec.md` e `specs/responsive-interface/spec.md`.

## Goals / Non-Goals

**Goals:**
- Estabelecer uma identidade visual consistente e reutilizável.
- Melhorar a hierarquia visual e a legibilidade das páginas.
- Definir padrões de responsividade e estados visuais.
- Reduzir duplicação de estilos e componentes quando isso for compatível com a arquitetura atual.
- Preservar o comportamento funcional existente.

**Non-Goals:**
- Reescrever o backend ou alterar regras de negócio.
- Inventar endpoints, campos ou contratos de API do Xano.
- Remover ou renomear rotas existentes.
- Introduzir dependências adicionais sem necessidade comprovada.
- Alterar autenticação, permissões ou persistência como parte exclusiva do redesign.

## Decisions

### 1. Inspecionar a arquitetura antes de alterar o frontend

A implementação começará pelo levantamento da estrutura de pastas, das páginas, dos componentes compartilhados, dos estilos e das dependências atuais.

**Motivo:** evita criar uma arquitetura paralela ou substituir funcionalidades que já existem.

**Alternativa considerada:** reconstruir as páginas do zero. Essa opção foi descartada inicialmente porque aumenta o risco de regressões e de perda da lógica existente.

### 2. Centralizar os padrões visuais

Cores, tipografia, espaçamentos, bordas, sombras e estados interativos deverão ser definidos de forma centralizada sempre que a arquitetura atual permitir.

A identidade visual deverá aproveitar a direção já estabelecida para o projeto: fundo escuro, tons de azul e verde como cores de destaque e tipografia legível. Os valores finais serão confirmados durante a inspeção e o planejamento visual.

**Motivo:** facilita a manutenção e mantém a consistência entre as páginas.

**Alternativa considerada:** definir estilos independentes para cada página. Essa abordagem foi descartada por favorecer inconsistências e duplicação.

### 3. Reutilizar componentes sem alterar suas responsabilidades

Elementos recorrentes, como botões, campos de formulário, cartões, navegação e mensagens de estado, deverão compartilhar componentes ou padrões visuais quando houver benefício claro.

A reutilização não deverá exigir mudanças desnecessárias na lógica de negócio ou nos dados recebidos pelas páginas.

**Motivo:** permite corrigir e evoluir a interface com menor esforço.

**Alternativa considerada:** criar um componente genérico para todos os elementos. Essa opção foi descartada porque abstrações excessivas podem dificultar a manutenção.

### 4. Tratar responsividade como requisito estrutural

Os layouts deverão se adaptar progressivamente a telas menores. Navegação, formulários, tabelas e ações administrativas serão avaliados individualmente para escolher o comportamento adequado em cada largura.

Quando uma tabela não puder ser apresentada integralmente em uma tela pequena, deverá ser adotada uma alternativa que mantenha os dados e as ações acessíveis, sem impor rolagem horizontal à página inteira.

**Motivo:** componentes diferentes precisam de adaptações distintas para continuar utilizáveis.

**Alternativa considerada:** apenas reduzir o tamanho de todos os elementos. Essa abordagem foi descartada por prejudicar a legibilidade e a usabilidade.

### 5. Preservar a integração existente e preparar a compatibilidade com o Xano

Os componentes visuais deverão continuar utilizando os mecanismos de dados e as funções existentes. Antes de modificar formulários ou fluxos que dependam de serviços externos, será necessário identificar suas entradas, saídas e tratamentos de erro.

A implementação não deverá presumir a estrutura futura da API do Xano. Ajustes de integração deverão ser tratados separadamente quando os contratos reais estiverem disponíveis.

**Motivo:** evita que o redesign introduza incompatibilidades ou simule comportamentos de backend não confirmados.

**Alternativa considerada:** substituir temporariamente as integrações por dados fictícios. Essa abordagem foi descartada como padrão porque poderia ocultar regressões.

### 6. Implementar e validar em etapas pequenas

A implementação deverá ocorrer por grupos de páginas e componentes, com verificações após cada grupo. As rotas, os formulários, a navegação e os estados funcionais existentes deverão ser conferidos antes da conclusão.

**Motivo:** facilita a identificação de regressões e permite corrigir problemas sem reescrever grandes partes do projeto.

**Alternativa considerada:** alterar todas as páginas em uma única etapa. Essa opção foi descartada pelo maior risco de erros difíceis de localizar.

## Risks / Trade-offs

- **Regressão de funcionalidades** → inspecionar a lógica existente e testar os fluxos após cada grupo de alterações.
- **Inconsistência visual residual** → utilizar padrões compartilhados e revisar todas as páginas contempladas.
- **Limitações de tabelas em telas pequenas** → avaliar alternativas responsivas sem ocultar informações ou ações essenciais.
- **Dependência de contratos externos ainda desconhecidos** → preservar os mecanismos existentes e adiar mudanças de integração até que a documentação do Xano esteja disponível.
- **Complexidade desnecessária de componentes** → abstrair somente padrões realmente recorrentes.
- **Diferenças entre o ambiente de desenvolvimento e o navegador** → validar a interface no aplicativo em execução e em diferentes larguras de tela.

## Migration Plan

1. Inspecionar a arquitetura e registrar as rotas e os fluxos existentes.
2. Definir os tokens visuais e os componentes compartilhados.
3. Implementar a identidade visual e os padrões comuns.
4. Atualizar as páginas públicas e de autenticação.
5. Atualizar o painel administrativo e suas páginas.
6. Validar responsividade, navegação, formulários e estados funcionais.
7. Corrigir regressões antes de considerar o redesign concluído.

As alterações deverão ser divididas em commits pequenos. Se uma etapa introduzir regressões, será possível reverter o commit correspondente e restaurar a versão funcional anterior.

## Open Questions

- Quais contratos e endpoints do Xano serão utilizados por cada página? A resposta será definida quando a documentação da API estiver disponível.
- Quais larguras de tela serão adotadas como referências para a validação responsiva? Deverão ser definidas durante a implementação, considerando os componentes reais e os dispositivos-alvo.
