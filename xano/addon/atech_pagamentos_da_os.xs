addon atech_pagamentos_da_os {
  input {
    int os_servicos_id
  }
  stack {
    db.query pagamento {
      where = $db.pagamento.os_servicos_id == $input.os_servicos_id
      sort = {id: "asc"}
      return = {type: "list"}
    }
  }
  guid = "yJhPu0JFNpWqBHiFBgx4VUZbfhs"
}
