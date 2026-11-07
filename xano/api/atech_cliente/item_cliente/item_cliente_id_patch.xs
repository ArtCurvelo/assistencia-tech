query "item_cliente/{item_cliente_id}" verb=PATCH {
  api_group = "atech_cliente"
  description = "Admin e atendente: edita um aparelho."
  auth = "user"
  input {
    int item_cliente_id {
      table = "item_cliente"
    }
    int cliente_id {
      table = "cliente"
    }
    text aparelho filters=trim
    text marca filters=trim
    text modelo filters=trim
    text? numero_serie? filters=trim
    text? observacoes? filters=trim
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "atendente"]}
    }
    db.get "item_cliente" {
      field_name = "id"
      field_value = $input.item_cliente_id
    } as $atual
    precondition ($atual != null) {
      error_type = "notfound"
      error = "Aparelho não encontrado."
    }
    db.edit "item_cliente" {
      field_name = "id"
      field_value = $input.item_cliente_id
      data = {
        cliente_id: $input.cliente_id,
        aparelho: $input.aparelho,
        marca: $input.marca,
        modelo: $input.modelo,
        numero_serie: $input.numero_serie,
        observacoes: $input.observacoes
      }
    } as $aparelho
  }
  response = $aparelho
}
