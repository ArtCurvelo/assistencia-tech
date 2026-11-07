query "portal/minha_conta" verb=GET {
  api_group = "atech_os"
  description = "Perfil cliente: o cadastro do cliente vinculado ao token."
  auth = "user"
  input {}
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["cliente"]}
    } as $eu
    precondition ($eu.cliente_id != null) {
      error_type = "accessdenied"
      error = "Sua conta não está vinculada a um cadastro de cliente."
    }
    db.get "cliente" {
      field_name = "id"
      field_value = $eu.cliente_id
    } as $cliente
    precondition ($cliente != null) {
      error_type = "notfound"
      error = "Cliente não encontrado."
    }
  }
  response = $cliente
}
