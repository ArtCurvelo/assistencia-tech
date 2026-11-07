query "cliente/{cliente_id}" verb=PATCH {
  api_group = "atech_cliente"
  description = "Admin e atendente: edita um cliente; CPF e e-mail continuam únicos."
  auth = "user"
  input {
    int cliente_id {
      table = "cliente"
    }
    text Nome filters=trim
    text Cpf filters=trim
    email email filters=trim|lower
    text telefone_Aparelho filters=trim
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "atendente"]}
    }
    db.get "cliente" {
      field_name = "id"
      field_value = $input.cliente_id
    } as $atual
    precondition ($atual != null) {
      error_type = "notfound"
      error = "Cliente não encontrado."
    }
    precondition (($input.Cpf|strlen) == 11) {
      error_type = "inputerror"
      error = "Informe o CPF com 11 dígitos."
    }
    db.query "cliente" {
      where = $db.cliente.Cpf == $input.Cpf && $db.cliente.id != $input.cliente_id
      return = {type: "exists"}
    } as $cpf_em_uso
    precondition (!$cpf_em_uso) {
      error_type = "inputerror"
      error = "Já existe um cliente com este CPF."
    }
    db.query "cliente" {
      where = $db.cliente.email == $input.email && $db.cliente.id != $input.cliente_id
      return = {type: "exists"}
    } as $email_em_uso
    precondition (!$email_em_uso) {
      error_type = "inputerror"
      error = "Já existe um cliente com este e-mail."
    }
    db.edit "cliente" {
      field_name = "id"
      field_value = $input.cliente_id
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
