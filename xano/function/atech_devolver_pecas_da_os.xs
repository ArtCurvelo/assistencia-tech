// Devolve ao estoque todas as peças do catálogo que estão no orçamento da ordem (cancelamento).
function "atech_devolver_pecas_da_os" {
  input {
    int os_servicos_id
    text autor
  }
  stack {
    db.query "os_itens" {
      where = $db.os_itens.os_servicos_id == $input.os_servicos_id && $db.os_itens.peca_id != null
      return = {type: "list"}
    } as $itens
    foreach ($itens) {
      each as $item {
        function.run "atech_mover_estoque" {
          input = {
            peca_id: $item.peca_id,
            tipo: "devolucao",
            quantidade: $item.quantidade,
            os_servicos_id: $input.os_servicos_id,
            autor: $input.autor,
            observacao: "Cancelamento da ordem"
          }
        }
      }
    }
  }
  response = $itens|count
}
