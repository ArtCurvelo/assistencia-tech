query "auth/me" verb=GET {
  api_group = "atech_auth"
  description = "Conta autenticada com perfil e vínculos."
  auth = "user"
  input {}
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "atendente", "tecnico", "cliente"]}
    }
    db.get "user" {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "name", "email", "role", "cliente_id", "especialidade", "ativo"]
    } as $usuario
  }
  response = $usuario
  guid = "NMPas5mZBy287Bd2YbOgewXDp5U"
}
