query "pecas" verb=GET {
  api_group = "atech_os"
  description = "Colaboradores: catálogo de peças do estoque."
  auth = "user"
  input {}
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "atendente", "tecnico"]}
    }
    db.query "peca" {
      sort = {nome: "asc"}
      return = {type: "list"}
      output = ["id", "codigo", "nome", "preco", "quantidade", "estoque_minimo", "ativo"]
    } as $pecas
  }
  response = $pecas
  guid = "ozJlhH7Yn1QDDHa_y_miKLnRCro"
}
