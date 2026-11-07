query "os_itens/{os_itens_id}" verb=DELETE {
  api_group = "atech_os"
  description = "Admin e técnico responsável: remove um item do orçamento (Em análise, Aguardando aprovação ou Em reparo)."
  auth = "user"
  input {
    int os_itens_id {
      table = "os_itens"
    }
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "tecnico"]}
    } as $eu
    db.get "os_itens" {
      field_name = "id"
      field_value = $input.os_itens_id
    } as $item
    precondition ($item != null) {
      error_type = "notfound"
      error = "Item do orçamento não encontrado."
    }
    db.get "os_servicos" {
      field_name = "id"
      field_value = $item.os_servicos_id
    } as $ordem
    precondition ($eu.role != "tecnico" || $ordem.user_id == $eu.id) {
      error_type = "accessdenied"
      error = "Esta ordem pertence a outro técnico; você pode apenas consultá-la."
    }
    precondition ($ordem.status == "em_analise" || $ordem.status == "aguardando_aprovacao" || $ordem.status == "em_reparo") {
      error_type = "inputerror"
      error = "O orçamento só pode ser alterado em Em análise, Aguardando aprovação e Em reparo."
    }
    function.run "atech_autor" {
      input = {user_id: $auth.id}
    } as $autor
    db.transaction {
      stack {
        conditional {
          if ($item.peca_id != null) {
            function.run "atech_mover_estoque" {
              input = {
                peca_id: $item.peca_id,
                tipo: "devolucao",
                quantidade: $item.quantidade,
                os_servicos_id: $ordem.id,
                autor: $autor,
                observacao: "Item removido do orçamento"
              }
            }
          }
        }
        db.del "os_itens" {
          field_name = "id"
          field_value = $input.os_itens_id
        }
        db.edit "os_servicos" {
          field_name = "id"
          field_value = $ordem.id
          data = {atualizado_em: now}
        }
      }
    }
  }
  response = {success: true}
  guid = "8KlMkQ_IIoWiUtYK3d-LixAgAp0"
}
