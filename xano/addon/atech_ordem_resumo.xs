addon atech_ordem_resumo {
  input {
    int os_servicos_id
  }
  stack {
    db.query os_servicos {
      where = $db.os_servicos.id == $input.os_servicos_id
      return = {type: "single"}
      output = ["id", "created_at"]
    }
  }
}
