// Avaliação do atendimento pelo cliente (add-service-rating): uma por ordem, imutável.
table "avaliacao" {
  auth = false
  schema {
    int id
    timestamp created_at?=now
    int os_servicos_id {
      table = "os_servicos"
    }
    int cliente_id {
      table = "cliente"
    }
    int nota
    text? comentario? filters=trim
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "os_servicos_id"}]}
  ]
  guid = "9DJlM2GqA088xxpnwE7c19f7OFo"
}
