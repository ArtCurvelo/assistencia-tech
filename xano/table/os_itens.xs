// Itens do orçamento da ordem de serviço (serviços e peças).
table "os_itens" {
  auth = false
  schema {
    int id
    timestamp created_at?=now
    int os_servicos_id {
      table = "os_servicos"
    }
    enum tipo {
      values = ["servico", "peca"]
    }
    text descricao filters=trim
    int quantidade?=1 filters=min:1
    decimal valor_unitario filters=min:0.01
    int? peca_id? {
      table = "peca"
      description = "Peça do catálogo de estoque; vazio para serviço e peça avulsa"
    }
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "os_servicos_id"}]}
  ]
  guid = "C7FdQg5ri9lpC4nV6VMCdtbr-H0"
}
