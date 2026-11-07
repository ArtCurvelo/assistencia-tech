// Ordem de serviço com itens, pagamentos e histórico (_itens, _pagamentos, _historico).
function "atech_ordem_completa" {
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
    db.query "os_itens" {
      where = $db.os_itens.os_servicos_id == $ordem.id
      sort = {id: "asc"}
      return = {type: "list"}
    } as $itens
    db.query "pagamento" {
      where = $db.pagamento.os_servicos_id == $ordem.id
      sort = {id: "asc"}
      return = {type: "list"}
    } as $pagamentos
    db.query "os_historico" {
      where = $db.os_historico.os_servicos_id == $ordem.id
      sort = {id: "asc"}
      return = {type: "list"}
    } as $historico
  }
  response = $ordem|set:"_itens":$itens|set:"_pagamentos":$pagamentos|set:"_historico":$historico
}
