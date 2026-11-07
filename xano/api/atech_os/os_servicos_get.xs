query "os_servicos" verb=GET {
  api_group = "atech_os"
  description = "Colaboradores: todas as ordens com itens, pagamentos e histórico."
  auth = "user"
  input {}
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "atendente", "tecnico"]}
    }
    db.query "os_servicos" {
      sort = {id: "desc"}
      return = {type: "list"}
      addon = [
        {name: "atech_itens_da_os", input: {os_servicos_id: $output.id}, as: "_itens"}
        {name: "atech_pagamentos_da_os", input: {os_servicos_id: $output.id}, as: "_pagamentos"}
        {name: "atech_historico_da_os", input: {os_servicos_id: $output.id}, as: "_historico"}
        {name: "atech_ordem_resumo", input: {os_servicos_id: $output.garantia_de}, as: "_garantia"}
      ]
    } as $ordens
  }
  response = $ordens
  guid = "uDqen-IF3Nm3t7Gl8ZO9ZmUU4Xo"
}
