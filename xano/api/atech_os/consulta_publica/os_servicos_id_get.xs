query "consulta_publica/{os_servicos_id}" verb=GET {
  api_group = "atech_os"
  description = "Consulta pública: somente status, aparelho, modelo e última atualização; sem dados pessoais nem valores."
  input {
    int os_servicos_id
  }
  stack {
    db.query "os_servicos" {
      join = {
        item_cliente: {
          table: "item_cliente",
          type: "inner",
          where: $db.os_servicos.item_cliente_id == $db.item_cliente.id
        }
      }
      eval = {
        aparelho: $db.item_cliente.aparelho,
        modelo: $db.item_cliente.modelo
      }
      where = $db.os_servicos.id == $input.os_servicos_id
      return = {type: "single"}
      output = ["id", "created_at", "status", "atualizado_em", "previsao_entrega", "aparelho", "modelo"]
    } as $ordem
    precondition ($ordem != null) {
      error_type = "notfound"
      error = "Ordem de serviço não encontrada."
    }
  }
  response = $ordem
  guid = "nlz7Z1_UGxTGovPDIUw3VRIlUdQ"
}
