query "portal/avaliacao" verb=POST {
  api_group = "atech_os"
  description = "Perfil cliente: avalia de 0 a 10 uma ordem própria entregue, uma única vez (add-service-rating)."
  auth = "user"
  input {
    int os_servicos_id
    int nota
    text? comentario? filters=trim
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["cliente"]}
    } as $eu
    db.get "os_servicos" {
      field_name = "id"
      field_value = $input.os_servicos_id
    } as $ordem
    precondition ($ordem != null && $eu.cliente_id != null && $ordem.cliente_id == $eu.cliente_id) {
      error_type = "notfound"
      error = "Ordem de serviço não encontrada."
    }
    precondition ($ordem.status == "entregue") {
      error_type = "inputerror"
      error = "Só ordens entregues podem ser avaliadas."
    }
    precondition ($input.nota >= 0 && $input.nota <= 10) {
      error_type = "inputerror"
      error = "A nota deve ser um número inteiro de 0 a 10."
    }
    precondition ($input.comentario == null || ($input.comentario|strlen) <= 500) {
      error_type = "inputerror"
      error = "O comentário deve ter no máximo 500 caracteres."
    }
    db.query "avaliacao" {
      where = $db.avaliacao.os_servicos_id == $ordem.id
      return = {type: "exists"}
    } as $ja_avaliada
    precondition (!$ja_avaliada) {
      error_type = "inputerror"
      error = "Esta ordem já foi avaliada."
    }
    db.add "avaliacao" {
      data = {
        os_servicos_id: $ordem.id,
        cliente_id: $eu.cliente_id,
        nota: $input.nota,
        comentario: $input.comentario
      }
    } as $avaliacao
  }
  response = $avaliacao
  guid = "CzhAnAfzF9wGJFG7N6xnJakFqVg"
}
