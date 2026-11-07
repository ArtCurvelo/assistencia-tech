// Movimenta o estoque de uma peça e registra a movimentação. Recusa quantidade negativa.
function "atech_mover_estoque" {
  input {
    int peca_id
    enum tipo {
      values = ["entrada", "saida", "devolucao"]
    }
    int quantidade
    int? os_servicos_id?
    text autor
    text? observacao?
  }
  stack {
    db.get "peca" {
      field_name = "id"
      field_value = $input.peca_id
    } as $peca
    precondition ($peca != null) {
      error_type = "notfound"
      error = "Peça não encontrada."
    }
    precondition ($input.quantidade > 0) {
      error_type = "inputerror"
      error = "A quantidade deve ser maior que zero."
    }
    var $saldo {
      value = $peca.quantidade + $input.quantidade
    }
    conditional {
      if ($input.tipo == "saida") {
        precondition ($peca.ativo) {
          error_type = "inputerror"
          error = "A peça está inativa e não pode ser usada em orçamentos."
        }
        precondition ($peca.quantidade >= $input.quantidade) {
          error_type = "inputerror"
          error = "Estoque insuficiente para a peça escolhida."
        }
        var.update $saldo {
          value = $peca.quantidade - $input.quantidade
        }
      }
    }
    db.edit "peca" {
      field_name = "id"
      field_value = $peca.id
      data = {quantidade: $saldo}
    } as $atualizada
    db.add "movimento_estoque" {
      data = {
        peca_id: $peca.id,
        tipo: $input.tipo,
        quantidade: $input.quantidade,
        os_servicos_id: $input.os_servicos_id,
        autor: $input.autor,
        observacao: $input.observacao
      }
    } as $movimento
  }
  response = $atualizada
  guid = "xJ-alUeMXmHs4k9hQaPQKNTB3PA"
}
