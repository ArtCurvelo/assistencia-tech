query "auth/login" verb=POST {
  api_group = "atech_auth"
  description = "Login por e-mail e senha. Recusa contas inativas."
  input {
    email email filters=trim|lower
    text password {
      sensitive = true
    }
  }
  stack {
    db.get "user" {
      field_name = "email"
      field_value = $input.email
    } as $usuario
    precondition ($usuario != null) {
      error_type = "accessdenied"
      error = "E-mail ou senha inválidos."
    }
    security.check_password {
      text_password = $input.password
      hash_password = $usuario.password
    } as $senha_ok
    precondition ($senha_ok) {
      error_type = "accessdenied"
      error = "E-mail ou senha inválidos."
    }
    precondition ($usuario.ativo) {
      error_type = "accessdenied"
      error = "E-mail ou senha inválidos."
    }
    security.create_auth_token {
      table = "user"
      id = $usuario.id
      extras = {role: $usuario.role}
      expiration = 86400
    } as $token
  }
  response = {authToken: $token, user_id: $usuario.id}
}
