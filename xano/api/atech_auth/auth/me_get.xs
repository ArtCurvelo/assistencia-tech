query "auth/me" verb=GET {
  api_group = "atech_auth"
  description = "Conta autenticada com perfil e vínculos."
  auth = "user"
  input {}
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "atendente", "tecnico", "cliente"]}
    } as $usuario
  }
  response = {
    id: $usuario.id,
    name: $usuario.name,
    email: $usuario.email,
    role: $usuario.role,
    cliente_id: $usuario.cliente_id,
    especialidade: $usuario.especialidade,
    ativo: $usuario.ativo
  }
  guid = "NMPas5mZBy287Bd2YbOgewXDp5U"
}
