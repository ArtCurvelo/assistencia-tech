query "pecas" verb=POST {
  api_group = "atech_os"
  description = "Admin e atendente: cadastra uma peça (quantidade inicial zero; código único)."
  auth = "user"
  input {
    text codigo filters=trim|upper
    text nome filters=trim
    decimal preco filters=min:0.01
    int? estoque_minimo?=0 filters=min:0
    bool? ativo?=true
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "atendente"]}
    }
    precondition ($input.codigo != "" && $input.nome != "") {
      error_type = "inputerror"
      error = "Informe o código e o nome da peça."
    }
    db.has "peca" {
      field_name = "codigo"
      field_value = $input.codigo
    } as $codigo_em_uso
    precondition (!$codigo_em_uso) {
      error_type = "inputerror"
      error = "Já existe uma peça com este código."
    }
    db.add "peca" {
      data = {
        codigo: $input.codigo,
        nome: $input.nome,
        preco: $input.preco,
        quantidade: 0,
        estoque_minimo: $input.estoque_minimo ?? 0,
        ativo: $input.ativo ?? true
      }
    } as $nova
    db.get "peca" {
      field_name = "id"
      field_value = $nova.id
      output = ["id", "codigo", "nome", "preco", "quantidade", "estoque_minimo", "ativo"]
    } as $peca
  }
  response = $peca
}
