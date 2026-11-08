addon atech_avaliacao_da_os {
  input {
    int os_servicos_id
  }
  stack {
    db.query avaliacao {
      where = $db.avaliacao.os_servicos_id == $input.os_servicos_id
      return = {type: "single"}
      output = ["id", "created_at", "nota", "comentario"]
    }
  }
  guid = "8YnzTql9ePzsfPrkVvTrxptc5lw"
}
