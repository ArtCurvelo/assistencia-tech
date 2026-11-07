// Ordens de serviço. user_id = técnico responsável.
table "os_servicos" {
  auth = false
  schema {
    int id
    timestamp created_at?=now
    timestamp? atualizado_em?
    int cliente_id {
      table = "cliente"
    }
    int item_cliente_id {
      table = "item_cliente"
    }
    int? user_id? {
      table = "user"
      description = "Técnico responsável"
    }
    text descricao_problema filters=trim
    text? diagnostico? filters=trim
    text? motivo_cancelamento? filters=trim
    date? previsao_entrega? {
      description = "Previsão de entrega (padrão: abertura + 7 dias)"
    }
    int? garantia_de? {
      table = "os_servicos"
      description = "Ordem original, nas ordens em garantia"
    }
    enum status?="recebido" {
      values = ["recebido", "em_analise", "aguardando_aprovacao", "em_reparo", "concluido", "entregue", "cancelado"]
    }
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "cliente_id"}]}
    {type: "btree", field: [{name: "user_id"}]}
    {type: "btree", field: [{name: "status"}]}
  ]
  guid = "-b1_liVZK_UlppVLL-FaHHozOhs"
}
