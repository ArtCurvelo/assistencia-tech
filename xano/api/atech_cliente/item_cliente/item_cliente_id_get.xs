query "item_cliente/{item_cliente_id}" verb=GET {
  api_group = "atech_cliente"
  description = "Colaboradores: consulta um aparelho."
  auth = "user"
  input {
    int item_cliente_id {
      table = "item_cliente"
    }
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "atendente", "tecnico"]}
    }
    db.get "item_cliente" {
      field_name = "id"
      field_value = $input.item_cliente_id
    } as $aparelho
    precondition ($aparelho != null) {
      error_type = "notfound"
      error = "Aparelho não encontrado."
    }
  }
  response = $aparelho
  guid = "0EqJasFzyPdQVvA-PLdojCxMDdI"
}
