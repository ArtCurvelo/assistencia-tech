query "os_servicos" verb=POST {
  api_group = "atech_os"
  description = "Admin e atendente: abre uma ordem (sempre em recebido) para um aparelho do cliente."
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
    db.add "os_servicos" {
      data = {
        cliente_id: $input.cliente_id,
        item_cliente_id: $input.item_cliente_id,
        descricao_problema: $input.descricao_problema,
        status: "recebido",
        atualizado_em: now
      }
    } as $ordem
  }
  response = $ordem
  guid = "SVfsp-P70qIOHWZL8l42uZj1tQ8"
}
