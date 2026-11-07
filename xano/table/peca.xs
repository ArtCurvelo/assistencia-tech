// Catálogo de peças do estoque. A quantidade só muda por movimentações.
table "peca" {
  auth = false
  schema {
    int id
    timestamp created_at?=now
    text codigo filters=trim|upper
    text nome filters=trim
    decimal preco filters=min:0.01
    int quantidade?=0 filters=min:0
    int estoque_minimo?=0 filters=min:0
    bool ativo?=true
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "codigo"}]}
  ]
}
