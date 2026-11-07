// Totais da ordem: soma dos itens, soma dos pagamentos e saldo a receber.
function "atech_saldo_da_os" {
  input {
    int os_servicos_id
  }
  stack {
    db.query "os_itens" {
      where = $db.os_itens.os_servicos_id == $input.os_servicos_id
      return = {type: "list"}
    } as $itens
    db.query "pagamento" {
      where = $db.pagamento.os_servicos_id == $input.os_servicos_id
      return = {type: "list"}
    } as $pagamentos
    var $total {
      value = 0
    }
    foreach ($itens) {
      each as $item {
        var.update $total {
          value = $total + ($item.quantidade * $item.valor_unitario)
        }
      }
    }
    var $pago {
      value = 0
    }
    foreach ($pagamentos) {
      each as $pagamento {
        var.update $pago {
          value = $pago + $pagamento.valor_a_ser_pago
        }
      }
    }
  }
  response = {total: $total, pago: $pago, saldo: $total - $pago, quantidade_itens: $itens|count}
}
