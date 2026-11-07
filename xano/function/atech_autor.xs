// Autor no formato da aplicação: "Nome (Perfil)".
function "atech_autor" {
  input {
    int user_id
  }
  stack {
    db.get "user" {
      field_name = "id"
      field_value = $input.user_id
    } as $usuario
    var $perfis {
      value = {admin: "Administrador", atendente: "Atendente", tecnico: "Técnico", cliente: "Cliente"}
    }
    var $autor {
      value = $usuario.name ~ " (" ~ ($perfis|get:$usuario.role:"Usuário") ~ ")"
    }
  }
  response = $autor
}
