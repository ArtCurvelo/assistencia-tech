query "item_cliente" verb=GET {
  api_group = "atech_cliente"
  description = "Colaboradores: lista os aparelhos."
  auth = "user"
  input {}
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "atendente", "tecnico"]}
    }
    db.query "item_cliente" {
      sort = {id: "asc"}
      return = {type: "list"}
    } as $aparelhos
  }
  response = $aparelhos
  guid = "kNwu42ypSm98cYCnppxQFlasoC8"
}
