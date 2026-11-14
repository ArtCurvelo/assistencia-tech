# Design: Direitos do titular (LGPD)

## Decisions

### D1. Anonimizar, não apagar

Apagar o cadastro quebraria as ordens, que a assistência precisa manter (garantia, fiscal, defesa em reclamações). O cadastro é anonimizado: `Nome` = "Cliente anonimizado", `Cpf` = `anonimizado-<id>`, `email` = `anonimizado-<id>@removido.invalid` (domínio reservado), `telefone_Aparelho` vazio e `anonimizado = true`. Os valores continuam únicos, como exigem os índices da tabela.

### D2. Leitura de cliente anonimizado

O modelo `Client` valida CPF, e-mail e telefone. Um registro com `anonimizado = true` é lido sem essas validações (`model_construct`), com campos pessoais vazios e `anonymized = True`; as telas mostram "Cliente anonimizado".

### D3. Confirmação e limites

A exclusão exige a senha da conta (conferida no servidor com `security.check_password`) e é recusada enquanto houver ordem em andamento (não Entregue nem Cancelada), porque o equipamento ainda está na assistência. O login é desativado (`ativo = false`); o e-mail e o nome da conta também são substituídos.

### D4. Avaliações

As notas continuam no NPS (dado estatístico, sem identificação após a anonimização); os comentários são apagados, porque podem conter informação pessoal.

### D5. Exportação no próprio portal

O arquivo é montado a partir das leituras que o portal já faz (`portal/minha_conta` e `portal/minhas_ordens`): nenhum endpoint novo, e só os dados do próprio cliente. Formato JSON, legível e reutilizável (portabilidade).

## Risks / Trade-offs

- [Exclusão irreversível] → confirmação com senha e aviso explícito antes; a equipe não consegue desfazer.
