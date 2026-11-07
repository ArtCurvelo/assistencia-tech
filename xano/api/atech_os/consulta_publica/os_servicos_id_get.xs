query "consulta_publica/{os_servicos_id}" verb=GET {
  api_group = "atech_os"
  description = "Consulta pública: somente status, aparelho, modelo e última atualização; sem dados pessoais nem valores."
  input {
    int os_servicos_id
  }
  stack {
    db.get "os_servicos" {
      field_name = "id"
      field_value = $input.os_servicos_id
    } as $ordem
    precondition ($ordem != null) {
      error_type = "notfound"
      error = "Ordem de serviço não encontrada."
    }
    db.get "item_cliente" {
      field_name = "id"
      field_value = $ordem.item_cliente_id
    } as $aparelho
  }
  response = {
    id: $ordem.id,
    status: $ordem.status,
    aparelho: $aparelho.aparelho,
    modelo: $aparelho.modelo,
    atualizado_em: $ordem.atualizado_em
  }
  guid = "nlz7Z1_UGxTGovPDIUw3VRIlUdQ"
}
