addon atech_historico_da_os {
  input {
    int os_servicos_id
  }
  stack {
    db.query os_historico {
      where = $db.os_historico.os_servicos_id == $input.os_servicos_id
      sort = {id: "asc"}
      return = {type: "list"}
    }
  }
}
