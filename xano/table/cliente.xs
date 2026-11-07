// Clientes da assistência. CPF e e-mail únicos.
table "cliente" {
  auth = false
  schema {
    int id
    timestamp created_at?=now
    text Nome filters=trim
    text Cpf filters=trim {
      sensitive = true
    }
    email email filters=trim|lower {
      sensitive = true
    }
    text telefone_Aparelho filters=trim {
      description = "Telefone do cliente"
    }
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "Cpf"}]}
    {type: "btree|unique", field: [{name: "email"}]}
  ]
}
