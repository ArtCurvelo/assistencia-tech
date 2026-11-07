query "usuarios" verb=GET {
  api_group = "atech_auth"
  description = "Somente admin: lista as contas (sem senha)."
  auth = "user"
  input {}
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin"]}
    }
    db.query "user" {
      sort = {name: "asc"}
      return = {type: "list"}
      output = ["id", "created_at", "name", "email", "role", "cliente_id", "especialidade", "ativo"]
    } as $usuarios
  }
  response = $usuarios
  guid = "Tb8IsYwyBYf4iJp3tGv_e5wkPqk"
}
