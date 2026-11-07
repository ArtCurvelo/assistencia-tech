query "auth/signup_cliente" verb=POST {
  api_group = "atech_auth"
  description = "Cadastro público: cria o cliente e a conta com perfil cliente na mesma transação."
  input {
    text Nome filters=trim
    text Cpf filters=trim
    email email filters=trim|lower
    text telefone_Aparelho filters=trim
    text password filters=min:8 {
      sensitive = true
    }
  }
  stack {
    precondition (($input.Cpf|strlen) == 11) {
      error_type = "inputerror"
      error = "Informe o CPF com 11 dígitos."
    }
    db.has "cliente" {
      field_name = "Cpf"
      field_value = $input.Cpf
    } as $cpf_em_uso
    precondition (!$cpf_em_uso) {
      error_type = "inputerror"
      error = "Já existe um cliente com este CPF."
    }
    db.has "cliente" {
      field_name = "email"
      field_value = $input.email
    } as $email_cliente_em_uso
    db.has "user" {
      field_name = "email"
      field_value = $input.email
    } as $email_conta_em_uso
    precondition (!$email_cliente_em_uso && !$email_conta_em_uso) {
      error_type = "inputerror"
      error = "Já existe uma conta com este e-mail."
    }
    db.transaction {
      stack {
        db.add "cliente" {
          data = {
            Nome: $input.Nome,
            Cpf: $input.Cpf,
            email: $input.email,
            telefone_Aparelho: $input.telefone_Aparelho
          }
        } as $cliente
        db.add "user" {
          data = {
            name: $input.Nome,
            email: $input.email,
            password: $input.password,
            role: "cliente",
            cliente_id: $cliente.id,
            ativo: true
          }
        } as $usuario
      }
    }
    security.create_auth_token {
      table = "user"
      id = $usuario.id
      extras = {role: "cliente"}
      expiration = 86400
    } as $token
  }
  response = {authToken: $token, user_id: $usuario.id}
}
