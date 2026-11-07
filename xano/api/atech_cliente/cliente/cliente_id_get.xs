query "cliente/{cliente_id}" verb=GET {
  api_group = "atech_cliente"
  description = "Colaboradores: consulta um cliente."
  auth = "user"
  input {
    int cliente_id {
      table = "cliente"
    }
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "atendente", "tecnico"]}
    }
    db.get "cliente" {
      field_name = "id"
      field_value = $input.cliente_id
    } as $cliente
    precondition ($cliente != null) {
      error_type = "notfound"
      error = "Cliente não encontrado."
    }
  }
  response = $cliente
}
