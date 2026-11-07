query "estoque/movimentos" verb=GET {
  api_group = "atech_os"
  description = "Colaboradores: movimentações de estoque, mais recentes primeiro, com a ordem relacionada (_ordem)."
  auth = "user"
  input {}
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "atendente", "tecnico"]}
    }
    db.query "movimento_estoque" {
      sort = {id: "desc"}
      return = {type: "list"}
      addon = [
        {name: "atech_ordem_resumo", input: {os_servicos_id: $output.os_servicos_id}, as: "_ordem"}
      ]
    } as $movimentos
  }
  response = $movimentos
}
