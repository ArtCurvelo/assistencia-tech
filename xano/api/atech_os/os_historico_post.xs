query "os_historico" verb=POST {
  api_group = "atech_os"
  description = "Colaboradores: registra um evento no histórico da ordem (somente inclusão)."
  auth = "user"
  input {
    int os_servicos_id {
      table = "os_servicos"
    }
    text autor filters=trim
    text tipo filters=trim
    text descricao filters=trim
    text? para_status? filters=trim
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "atendente", "tecnico"]}
    }
    db.has "os_servicos" {
      field_name = "id"
      field_value = $input.os_servicos_id
    } as $ordem_existe
    precondition ($ordem_existe) {
      error_type = "notfound"
      error = "Ordem de serviço não encontrada."
    }
    precondition ($input.descricao != "" && $input.tipo != "" && $input.autor != "") {
      error_type = "inputerror"
      error = "Autor, tipo e descrição do evento são obrigatórios."
    }
    db.add "os_historico" {
      data = {
        os_servicos_id: $input.os_servicos_id,
        autor: $input.autor,
        tipo: $input.tipo,
        descricao: $input.descricao,
        para_status: $input.para_status
      }
    } as $evento
  }
  response = $evento
}
