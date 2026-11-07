query "os_servicos/{os_servicos_id}" verb=PATCH {
  api_group = "atech_os"
  description = "Colaboradores: atribui o técnico, registra o diagnóstico ou muda o status, com as regras do fluxo da ordem."
  auth = "user"
  input {
    int os_servicos_id {
      table = "os_servicos"
    }
    enum? status? {
      values = ["recebido", "em_analise", "aguardando_aprovacao", "em_reparo", "concluido", "entregue", "cancelado"]
    }
    int? user_id? {
      table = "user"
    }
    text? diagnostico? filters=trim
    text? motivo_cancelamento? filters=trim
    timestamp? atualizado_em? {
      description = "Ignorado: o servidor sempre grava o horário atual."
    }
    date? previsao_entrega?
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "atendente", "tecnico"]}
    } as $eu
    db.get "os_servicos" {
      field_name = "id"
      field_value = $input.os_servicos_id
    } as $atual
    precondition ($atual != null) {
      error_type = "notfound"
      error = "Ordem de serviço não encontrada."
    }
    precondition ($eu.role != "tecnico" || $atual.user_id == $eu.id) {
      error_type = "accessdenied"
      error = "Esta ordem pertence a outro técnico; você pode apenas consultá-la."
    }
    var $updates {
      value = {atualizado_em: now}
    }
    var $tecnico_final {
      value = $atual.user_id
    }
    var $diagnostico_final {
      value = $atual.diagnostico
    }

    // Técnico responsável: admin e atendente, fora de entregue/cancelado.
    conditional {
      if ($input.user_id != null && $input.user_id != $atual.user_id) {
        precondition ($eu.role != "tecnico") {
          error_type = "accessdenied"
          error = "O perfil tecnico não tem permissão para atribuir o técnico responsável."
        }
        precondition ($atual.status != "entregue" && $atual.status != "cancelado") {
          error_type = "inputerror"
          error = "O técnico não pode ser alterado com a ordem entregue ou cancelada."
        }
        db.get "user" {
          field_name = "id"
          field_value = $input.user_id
        } as $novo_tecnico
        precondition ($novo_tecnico != null && $novo_tecnico.role == "tecnico" && $novo_tecnico.ativo) {
          error_type = "inputerror"
          error = "Selecione um técnico ativo."
        }
        var.update $updates.user_id {
          value = $input.user_id
        }
        var.update $tecnico_final {
          value = $input.user_id
        }
      }
    }

    // Diagnóstico: admin e técnico, em em_analise, aguardando_aprovacao ou em_reparo.
    conditional {
      if ($input.diagnostico != null && $input.diagnostico != $atual.diagnostico) {
        precondition ($eu.role != "atendente") {
          error_type = "accessdenied"
          error = "O perfil atendente não tem permissão para registrar diagnóstico e orçamento."
        }
        precondition ($atual.status == "em_analise" || $atual.status == "aguardando_aprovacao" || $atual.status == "em_reparo") {
          error_type = "inputerror"
          error = "O diagnóstico só pode ser alterado em Em análise, Aguardando aprovação e Em reparo."
        }
        precondition ($input.diagnostico != "") {
          error_type = "inputerror"
          error = "Preencha o campo obrigatório: Diagnóstico."
        }
        var.update $updates.diagnostico {
          value = $input.diagnostico
        }
        var.update $diagnostico_final {
          value = $input.diagnostico
        }
      }
    }

    // Previsão de entrega: admin e atendente, fora de entregue/cancelado (add-deadlines-and-warranty).
    conditional {
      if ($input.previsao_entrega != null && $input.previsao_entrega != $atual.previsao_entrega) {
        precondition ($eu.role != "tecnico") {
          error_type = "accessdenied"
          error = "O perfil tecnico não tem permissão para alterar a previsão de entrega."
        }
        precondition ($atual.status != "entregue" && $atual.status != "cancelado") {
          error_type = "inputerror"
          error = "A previsão de entrega não pode ser alterada com a ordem entregue ou cancelada."
        }
        precondition ($input.previsao_entrega >= ($atual.created_at|format_timestamp:"Y-m-d":"America/Sao_Paulo")) {
          error_type = "inputerror"
          error = "A previsão de entrega não pode ser anterior à data de abertura."
        }
        var.update $updates.previsao_entrega {
          value = $input.previsao_entrega
        }
      }
    }

    // Status: transições permitidas, permissão por perfil e pré-condições.
    conditional {
      if ($input.status != null && $input.status != $atual.status) {
        precondition ($atual.status != "entregue") {
          error_type = "inputerror"
          error = "A ordem já foi entregue e está finalizada; o status não pode mais ser alterado."
        }
        var $transicoes {
          value = {
            recebido: ["em_analise", "cancelado"],
            em_analise: ["aguardando_aprovacao", "cancelado"],
            aguardando_aprovacao: ["em_reparo", "cancelado"],
            em_reparo: ["concluido", "cancelado"],
            concluido: ["entregue"],
            cancelado: ["entregue"]
          }
        }
        precondition (($transicoes|get:$atual.status:[])|in:$input.status) {
          error_type = "inputerror"
          error = "Transição de status não permitida a partir do status atual."
        }
        conditional {
          if ($input.status == "cancelado" || $input.status == "entregue" || ($atual.status == "aguardando_aprovacao" && $input.status == "em_reparo")) {
            precondition ($eu.role != "tecnico") {
              error_type = "accessdenied"
              error = "O perfil tecnico não tem permissão para aprovar, entregar ou cancelar ordens."
            }
          }
          else {
            precondition ($eu.role != "atendente") {
              error_type = "accessdenied"
              error = "O perfil atendente não tem permissão para alterar o status técnico da ordem."
            }
          }
        }
        function.run "atech_saldo_da_os" {
          input = {os_servicos_id: $atual.id}
        } as $totais
        precondition ($input.status != "em_analise" || $tecnico_final != null) {
          error_type = "inputerror"
          error = "Atribua um técnico responsável antes de iniciar a análise."
        }
        precondition ($input.status != "aguardando_aprovacao" || ($diagnostico_final != null && $diagnostico_final != "")) {
          error_type = "inputerror"
          error = "Registre o diagnóstico técnico antes de enviar para aprovação."
        }
        precondition ($input.status != "aguardando_aprovacao" || $totais.quantidade_itens > 0) {
          error_type = "inputerror"
          error = "O orçamento precisa ter ao menos um item antes de ser enviado para aprovação."
        }
        precondition ($input.status != "entregue" || $atual.status != "concluido" || $totais.saldo <= 0) {
          error_type = "inputerror"
          error = "Há saldo a receber. Registre o pagamento antes da entrega."
        }
        conditional {
          if ($input.status == "cancelado") {
            precondition ($input.motivo_cancelamento != null && $input.motivo_cancelamento != "") {
              error_type = "inputerror"
              error = "Informe o motivo do cancelamento."
            }
            var.update $updates.motivo_cancelamento {
              value = $input.motivo_cancelamento
            }
          }
        }
        var.update $updates.status {
          value = $input.status
        }
      }
    }

    function.run "atech_autor" {
      input = {user_id: $auth.id}
    } as $autor
    db.transaction {
      stack {
        conditional {
          if ($input.status == "cancelado" && $atual.status != "cancelado") {
            function.run "atech_devolver_pecas_da_os" {
              input = {os_servicos_id: $atual.id, autor: $autor}
            }
          }
        }
        db.patch "os_servicos" {
          field_name = "id"
          field_value = $input.os_servicos_id
          data = $updates
        } as $alterada
      }
    }
    db.get "os_servicos" {
      field_name = "id"
      field_value = $input.os_servicos_id
    } as $ordem
  }
  response = $ordem
  guid = "KLA_6aOWohwbu_K_xaHCSaoEufI"
}
