// Busca o usuário do token, exige conta ativa e um dos perfis informados.
// Consulta o banco a cada chamada: mudanças de perfil e desativação valem na hora.
function "atech_usuario_autorizado" {
  input {
    int user_id
    text[] roles
  }
  stack {
    db.get "user" {
      field_name = "id"
      field_value = $input.user_id
    } as $usuario
    precondition ($usuario != null) {
      error_type = "accessdenied"
      error = "Conta não encontrada."
    }
    precondition ($usuario.ativo) {
      error_type = "accessdenied"
      error = "Conta inativa."
    }
    precondition ($input.roles|in:$usuario.role) {
      error_type = "accessdenied"
      error = "Seu perfil não tem permissão para esta ação."
    }
  }
  response = $usuario|unset:"password"
}
