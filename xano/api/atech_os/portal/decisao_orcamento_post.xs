query "portal/decisao_orcamento" verb=POST {
  api_group = "atech_os"
  description = "Perfil cliente: aprova (em_reparo) ou recusa com motivo (cancelado) o orçamento de uma ordem própria em aguardando_aprovacao."
  auth = "user"
  input {
    int os_servicos_id
    bool aprovar
    text? motivo? filters=trim
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["cliente"]}
    } as $eu
    db.get "os_servicos" {
      field_name = "id"
      field_value = $input.os_servicos_id
    } as $atual
    precondition ($atual != null && $eu.cliente_id != null && $atual.cliente_id == $eu.cliente_id) {
      error_type = "notfound"
      error = "Ordem de serviço não encontrada."
    }
    precondition ($atual.status == "aguardando_aprovacao") {
      error_type = "inputerror"
      error = "Esta ordem não está aguardando a sua aprovação."
    }
    precondition ($input.aprovar || ($input.motivo != null && $input.motivo != "")) {
      error_type = "inputerror"
      error = "Informe o motivo da recusa."
    }
    var $autor {
      value = $eu.name ~ " (Cliente)"
    }
    var $decisao {
      value = "Orçamento aprovado pelo cliente."
    }
    var $novo_status {
      value = "em_reparo"
    }
    var $rotulo {
      value = "Em reparo"
    }
    var $mudanca {
      value = "Status alterado de Aguardando aprovação para Em reparo."
    }
    var $dados {
      value = {status: "em_reparo", atualizado_em: now}
    }
    conditional {
      if (!$input.aprovar) {
        var.update $decisao {
          value = "Orçamento recusado pelo cliente. Motivo: " ~ $input.motivo
        }
        var.update $novo_status {
          value = "cancelado"
        }
        var.update $rotulo {
          value = "Cancelado"
        }
        var.update $mudanca {
          value = "Status alterado de Aguardando aprovação para Cancelado. Motivo: Orçamento recusado pelo cliente: " ~ $input.motivo
        }
        var.update $dados {
          value = {
            status: "cancelado",
            motivo_cancelamento: "Orçamento recusado pelo cliente: " ~ $input.motivo,
            atualizado_em: now
          }
        }
      }
    }
    db.transaction {
      stack {
        db.add "os_historico" {
          data = {
            os_servicos_id: $atual.id,
            autor: $autor,
            tipo: "Decisão do cliente",
            descricao: $decisao,
            para_status: ""
          }
        } as $evento_decisao
        db.patch "os_servicos" {
          field_name = "id"
          field_value = $atual.id
          data = $dados
        } as $ordem_alterada
        db.add "os_historico" {
          data = {
            os_servicos_id: $atual.id,
            autor: $autor,
            tipo: "Status",
            descricao: $mudanca,
            para_status: $rotulo
          }
        } as $evento_status
      }
    }
    db.get "os_servicos" {
      field_name = "id"
      field_value = $atual.id
    } as $ordem
  }
  response = $ordem
  guid = "0CmmiQxOOxzNZ7pfW-QYe0KqAkM"
}
