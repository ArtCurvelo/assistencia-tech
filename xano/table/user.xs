// Contas de acesso. Perfis: admin, atendente, tecnico, cliente.
table "user" {
  auth = true
  schema {
    int id
    timestamp created_at?=now
    text name filters=trim
    email email filters=trim|lower {
      sensitive = true
    }
    password password {
      sensitive = true
    }
    enum role?="cliente" {
      values = ["admin", "atendente", "tecnico", "cliente"]
    }
    int? cliente_id? {
      table = "cliente"
      description = "Cliente vinculado (somente role cliente)"
    }
    text? especialidade? filters=trim
    bool ativo?=true
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "email"}]}
    {type: "btree", field: [{name: "role"}]}
  ]
}
