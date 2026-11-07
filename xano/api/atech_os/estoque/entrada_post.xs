query "estoque/entrada" verb=POST {
  api_group = "atech_os"
  description = "Admin e atendente: registra a entrada de unidades de uma peça, com movimentação."
  auth = "user"
  input {
    int peca_id
    int quantidade filters=min:1
    text? observacao? filters=trim
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "atendente"]}
    }
    function.run "atech_autor" {
      input = {user_id: $auth.id}
    } as $autor
    db.transaction {
      stack {
        function.run "atech_mover_estoque" {
          input = {
            peca_id: $input.peca_id,
            tipo: "entrada",
            quantidade: $input.quantidade,
            autor: $autor,
            observacao: $input.observacao
          }
        }
      }
    }
    db.get "peca" {
      field_name = "id"
      field_value = $input.peca_id
      output = ["id", "codigo", "nome", "preco", "quantidade", "estoque_minimo", "ativo"]
    } as $peca
  }
  response = $peca
}
