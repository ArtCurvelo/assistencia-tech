query "cliente/{cliente_id}" verb=DELETE {
  api_group = "atech_cliente"
  description = "Somente admin: exclui um cliente sem aparelhos nem ordens."
  auth = "user"
  input {
    int cliente_id {
      table = "cliente"
    }
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin"]}
    }
    db.query "item_cliente" {
      where = $db.item_cliente.cliente_id == $input.cliente_id
      return = {type: "exists"}
    } as $tem_aparelhos
    db.query "os_servicos" {
      where = $db.os_servicos.cliente_id == $input.cliente_id
      return = {type: "exists"}
    } as $tem_ordens
    precondition (!$tem_aparelhos && !$tem_ordens) {
      error_type = "inputerror"
      error = "Não é possível excluir: o cliente possui aparelhos ou ordens vinculados."
    }
    db.del "cliente" {
      field_name = "id"
      field_value = $input.cliente_id
    }
  }
  response = {success: true}
}
