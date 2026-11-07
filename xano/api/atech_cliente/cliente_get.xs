query "cliente" verb=GET {
  api_group = "atech_cliente"
  description = "Colaboradores: lista paginada de clientes, com busca por nome, CPF, e-mail ou telefone."
  auth = "user"
  input {
    text? busca? filters=trim
    int page?=1 filters=min:1
    int per_page?=100 filters=min:1|max:1000
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "atendente", "tecnico"]}
    }
    var $termo {
      value = $input.busca ?? ""
    }
    db.query "cliente" {
      where = $db.cliente.Nome includes $termo || $db.cliente.Cpf includes $termo || $db.cliente.email includes $termo || $db.cliente.telefone_Aparelho includes $termo
      sort = {Nome: "asc"}
      return = {type: "list", paging: {page: $input.page, per_page: $input.per_page}}
    } as $clientes
  }
  response = $clientes
  guid = "qHY8or6-cN1rtpMM6xwnmzkDOr8"
}
