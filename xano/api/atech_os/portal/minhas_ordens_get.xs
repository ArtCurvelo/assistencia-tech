query "portal/minhas_ordens" verb=GET {
  api_group = "atech_os"
  description = "Perfil cliente: somente as ordens do cliente vinculado ao token."
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
    db.query "os_servicos" {
      where = $db.os_servicos.cliente_id == $eu.cliente_id
      sort = {id: "desc"}
      return = {type: "list"}
      addon = [
        {name: "atech_itens_da_os", input: {os_servicos_id: $output.id}, as: "items._itens"}
        {name: "atech_pagamentos_da_os", input: {os_servicos_id: $output.id}, as: "items._pagamentos"}
        {name: "atech_historico_da_os", input: {os_servicos_id: $output.id}, as: "items._historico"}
      ]
    } as $ordens
  }
  response = $ordens
}
