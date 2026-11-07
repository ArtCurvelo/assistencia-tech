query "os_servicos" verb=POST {
  api_group = "atech_os"
  description = "Admin e atendente: abre uma ordem (sempre em recebido) para um aparelho do cliente; previsão padrão de 7 dias; garantia_de liga a ordem à original (até 90 dias da entrega)."
  auth = "user"
  input {
    int cliente_id {
      table = "cliente"
    }
    int item_cliente_id {
      table = "item_cliente"
    }
    text descricao_problema filters=trim
    enum? status?="recebido" {
      values = ["recebido", "em_analise", "aguardando_aprovacao", "em_reparo", "concluido", "entregue", "cancelado"]
    }
    date? previsao_entrega?
    int? garantia_de?
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin", "atendente"]}
    }
    precondition ($input.status == null || $input.status == "recebido") {
      error_type = "inputerror"
      error = "Toda ordem é aberta com o status recebido."
    }
    precondition ($input.descricao_problema != "") {
      error_type = "inputerror"
      error = "Preencha o campo obrigatório: Descrição do problema."
    }
    db.get "item_cliente" {
      field_name = "id"
      field_value = $input.item_cliente_id
    } as $aparelho
    precondition ($aparelho != null) {
      error_type = "notfound"
      error = "Aparelho não encontrado."
    }
    precondition ($aparelho.cliente_id == $input.cliente_id) {
      error_type = "inputerror"
      error = "O aparelho informado não pertence a este cliente."
    }
    var $hoje {
      value = now|format_timestamp:"Y-m-d":"America/Sao_Paulo"
    }
    var $previsao {
      value = $input.previsao_entrega ?? (now|transform_timestamp:"+7 days"|format_timestamp:"Y-m-d":"America/Sao_Paulo")
    }
    precondition ($previsao >= $hoje) {
      error_type = "inputerror"
      error = "A previsão de entrega não pode ser anterior à data de abertura."
    }
    conditional {
      if ($input.garantia_de != null) {
        function.run "atech_garantia_valida" {
          input = {
            os_servicos_id: $input.garantia_de,
            cliente_id: $input.cliente_id,
            item_cliente_id: $input.item_cliente_id
          }
        }
      }
    }
    db.add "os_servicos" {
      data = {
        cliente_id: $input.cliente_id,
        item_cliente_id: $input.item_cliente_id,
        descricao_problema: $input.descricao_problema,
        status: "recebido",
        atualizado_em: now,
        previsao_entrega: $previsao,
        garantia_de: $input.garantia_de
      }
    } as $ordem
  }
  response = $ordem
  guid = "SVfsp-P70qIOHWZL8l42uZj1tQ8"
}
