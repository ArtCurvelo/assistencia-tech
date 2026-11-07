// Aparelhos (equipamentos) dos clientes.
table "item_cliente" {
  auth = false
  schema {
    int id
    timestamp created_at?=now
    int cliente_id {
      table = "cliente"
    }
    text aparelho filters=trim {
      description = "Computador, Notebook, Console, Celular, Tablet ou Outro"
    }
    text marca filters=trim
    text modelo filters=trim
    text? numero_serie? filters=trim
    text? observacoes? filters=trim
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "cliente_id"}]}
  ]
  guid = "giw97OkXbLo0zNSVK99o2YUinGg"
}
