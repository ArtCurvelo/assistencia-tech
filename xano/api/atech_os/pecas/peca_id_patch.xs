query "pecas/{peca_id}" verb=PATCH {
  api_group = "atech_os"
  description = "Admin e atendente: edita código, nome, preço, mínimo e situação da peça; nunca a quantidade."
  auth = "user"
  input {
    int peca_id {
      table = "peca"
    }
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
    db.get "peca" {
      field_name = "id"
      field_value = $input.peca_id
    } as $atual
    precondition ($atual != null) {
      error_type = "notfound"
      error = "Peça não encontrada."
    }
    db.query "peca" {
      where = $db.peca.codigo == $input.codigo && $db.peca.id != $input.peca_id
      return = {type: "exists"}
    } as $codigo_em_uso
    precondition (!$codigo_em_uso) {
      error_type = "inputerror"
      error = "Já existe uma peça com este código."
    }
    db.edit "peca" {
      field_name = "id"
      field_value = $input.peca_id
      data = {
        codigo: $input.codigo,
        nome: $input.nome,
        preco: $input.preco,
        estoque_minimo: $input.estoque_minimo ?? 0,
        ativo: $input.ativo ?? true
      }
    } as $editada
    db.get "peca" {
      field_name = "id"
      field_value = $input.peca_id
      output = ["id", "codigo", "nome", "preco", "quantidade", "estoque_minimo", "ativo"]
    } as $peca
  }
  response = $peca
}
