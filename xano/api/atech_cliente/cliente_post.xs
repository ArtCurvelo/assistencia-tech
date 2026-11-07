query "cliente" verb=POST {
  api_group = "atech_cliente"
  description = "Admin e atendente: cadastra um cliente; CPF e e-mail únicos."
  auth = "user"
  input {
    text Nome filters=trim
    text Cpf filters=trim
    email email filters=trim|lower
    text telefone_Aparelho filters=trim
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "atendente"]}
    }
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
    } as $email_em_uso
    precondition (!$email_em_uso) {
      error_type = "inputerror"
      error = "Já existe um cliente com este e-mail."
    }
    db.add "cliente" {
      data = {
        Nome: $input.Nome,
        Cpf: $input.Cpf,
        email: $input.email,
        telefone_Aparelho: $input.telefone_Aparelho
      }
    } as $cliente
  }
  response = $cliente
}
