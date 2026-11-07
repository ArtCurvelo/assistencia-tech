query "item_cliente" verb=POST {
  api_group = "atech_cliente"
  description = "Admin e atendente: cadastra um aparelho de um cliente existente."
  auth = "user"
  input {
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
    db.has "cliente" {
      field_name = "id"
      field_value = $input.cliente_id
    } as $cliente_existe
    precondition ($cliente_existe) {
      error_type = "notfound"
      error = "Cliente não encontrado."
    }
    db.add "item_cliente" {
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
