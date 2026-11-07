query "os_servicos/{os_servicos_id}" verb=GET {
  api_group = "atech_os"
  description = "Colaboradores: uma ordem com itens, pagamentos e histórico."
  auth = "user"
  input {
    int os_servicos_id {
      table = "os_servicos"
    }
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "atendente", "tecnico"]}
    }
    function.run "atech_ordem_completa" {
      input = {os_servicos_id: $input.os_servicos_id}
    } as $ordem
  }
  response = $ordem
  guid = "BI12zg0W53_XvyUKigJX9j7XqCg"
}
