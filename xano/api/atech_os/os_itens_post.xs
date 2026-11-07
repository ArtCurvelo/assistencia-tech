query "os_itens" verb=POST {
  api_group = "atech_os"
  description = "Admin e técnico responsável: adiciona serviço ou peça ao orçamento (Em análise, Aguardando aprovação ou Em reparo)."
  auth = "user"
  input {
    int os_servicos_id {
      table = "os_servicos"
    }
    enum tipo {
      values = ["servico", "peca"]
    }
    text descricao filters=trim
    int? quantidade?=1 filters=min:1
    decimal valor_unitario filters=min:0.01
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "tecnico"]}
    } as $eu
    db.get "os_servicos" {
      field_name = "id"
      field_value = $input.os_servicos_id
    } as $ordem
    precondition ($ordem != null) {
      error_type = "notfound"
      error = "Ordem de serviço não encontrada."
    }
    precondition ($eu.role != "tecnico" || $ordem.user_id == $eu.id) {
      error_type = "accessdenied"
      error = "Esta ordem pertence a outro técnico; você pode apenas consultá-la."
    }
    precondition ($ordem.status == "em_analise" || $ordem.status == "aguardando_aprovacao" || $ordem.status == "em_reparo") {
      error_type = "inputerror"
      error = "O orçamento só pode ser alterado em Em análise, Aguardando aprovação e Em reparo."
    }
    precondition ($input.descricao != "") {
      error_type = "inputerror"
      error = "Preencha o campo obrigatório: Descrição."
    }
    var $quantidade {
      value = $input.quantidade ?? 1
    }
    conditional {
      if ($input.tipo == "servico") {
        var.update $quantidade {
          value = 1
        }
      }
    }
    db.add "os_itens" {
      data = {
        os_servicos_id: $input.os_servicos_id,
        tipo: $input.tipo,
        descricao: $input.descricao,
        quantidade: $quantidade,
        valor_unitario: $input.valor_unitario
      }
    } as $item
    db.edit "os_servicos" {
      field_name = "id"
      field_value = $input.os_servicos_id
      data = {atualizado_em: now}
    }
  }
  response = $item
  guid = "6grGXRQatg1njM_Q2Y-Q_BEgvHU"
}
