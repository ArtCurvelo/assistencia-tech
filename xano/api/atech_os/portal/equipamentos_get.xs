query "portal/equipamentos" verb=GET {
  api_group = "atech_os"
  description = "Perfil cliente: somente os aparelhos do cliente vinculado ao token (add-client-self-service)."
  auth = "user"
  input {}
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["cliente"]}
    } as $eu
    precondition ($eu.cliente_id != null) {
      error_type = "accessdenied"
      error = "Sua conta não está vinculada a um cadastro de cliente."
    }
    db.query "item_cliente" {
      where = $db.item_cliente.cliente_id == $eu.cliente_id
      sort = {id: "asc"}
      return = {type: "list"}
    } as $aparelhos
  }
  response = $aparelhos
  guid = "oZtqkdkJlyeyyqcs4I4oLAbWcCU"
}
