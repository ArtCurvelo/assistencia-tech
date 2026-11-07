addon atech_itens_da_os {
  input {
    int os_servicos_id
  }
  stack {
    db.query os_itens {
      where = $db.os_itens.os_servicos_id == $input.os_servicos_id
      sort = {id: "asc"}
      return = {type: "list"}
    }
  }
  guid = "NTHaS74SocKa_-gHgF8dpYbPkW0"
}
