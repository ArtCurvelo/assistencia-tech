query "usuarios" verb=POST {
  api_group = "atech_auth"
  description = "Somente admin: cria um colaborador."
  auth = "user"
  input {
    text name filters=trim
    email email filters=trim|lower
    text password filters=min:8 {
      sensitive = true
    }
    enum role {
      values = ["admin", "atendente", "tecnico", "cliente"]
    }
    text? especialidade? filters=trim
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin"]}
    }
    db.has "user" {
      field_name = "email"
      field_value = $input.email
    } as $email_em_uso
    precondition (!$email_em_uso) {
      error_type = "inputerror"
      error = "Já existe uma conta com este e-mail."
    }
    db.add "user" {
      data = {
        name: $input.name,
        email: $input.email,
        password: $input.password,
        role: $input.role,
        especialidade: $input.especialidade,
        ativo: true
      }
    } as $novo
  }
  response = $novo|unset:"password"
}
