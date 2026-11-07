query "tecnicos" verb=GET {
  api_group = "atech_auth"
  description = "Colaboradores: técnicos para atribuição e histórico."
  auth = "user"
  input {}
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "atendente", "tecnico"]}
    }
    db.query "user" {
      where = $db.user.role == "tecnico"
      sort = {name: "asc"}
      return = {type: "list"}
    } as $tecnicos
  }
  response = $tecnicos|map:($$|unset:"password"|unset:"email"|unset:"cliente_id")
  guid = "rV6FqEIEahlgppLLLdZqNOiJfpY"
}
