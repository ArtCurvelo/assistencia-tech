query "item_cliente/{item_cliente_id}" verb=DELETE {
  api_group = "atech_cliente"
  description = "Somente admin: exclui um aparelho sem ordens."
  auth = "user"
  input {
    int item_cliente_id {
      table = "item_cliente"
    }
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin"]}
    }
    db.query "os_servicos" {
      where = $db.os_servicos.item_cliente_id == $input.item_cliente_id
      return = {type: "exists"}
    } as $tem_ordens
    precondition (!$tem_ordens) {
      error_type = "inputerror"
      error = "Não é possível excluir: há ordens de serviço para este aparelho."
    }
    db.del "item_cliente" {
      field_name = "id"
      field_value = $input.item_cliente_id
    }
  }
  response = {success: true}
  guid = "65RB4zPL7YiVKrlF-PrSW-EW_Pg"
}
