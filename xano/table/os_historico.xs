// Histórico imutável da ordem de serviço (somente inclusão).
table "os_historico" {
  auth = false
  schema {
    int id
    timestamp created_at?=now
    int os_servicos_id {
      table = "os_servicos"
    }
    text autor filters=trim
    text tipo filters=trim
    text descricao filters=trim
    text? para_status? filters=trim
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "os_servicos_id"}, {name: "created_at"}]}
  ]
  guid = "7M4TxPu8Y88M9rzGNolpkysTHIs"
}
