query "portal/solicitacao" verb=POST {
  api_group = "atech_os"
  description = "Perfil cliente: solicita atendimento para um aparelho próprio. A ordem nasce em solicitado, sem previsão, com a forma de entrega (loja ou motoboy) e o evento de abertura no histórico (add-client-self-service)."
  auth = "user"
  input {
    int item_cliente_id
    text descricao_problema filters=trim
    enum entrega_modo {
      values = ["loja", "motoboy"]
    }
    text? coleta_endereco? filters=trim
    text? coleta_periodo? filters=trim
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["cliente"]}
    } as $eu
    precondition ($eu.cliente_id != null) {
      error_type = "accessdenied"
      error = "Sua conta não está vinculada a um cadastro de cliente."
    }
    db.get "item_cliente" {
      field_name = "id"
      field_value = $input.item_cliente_id
    } as $aparelho
    precondition ($aparelho != null && $aparelho.cliente_id == $eu.cliente_id) {
      error_type = "notfound"
      error = "Equipamento não encontrado."
    }
    precondition ($input.descricao_problema != "") {
      error_type = "inputerror"
      error = "Descreva o problema do equipamento."
    }
    var $endereco {
      value = null
    }
    var $periodo {
      value = null
    }
    var $entrega {
      value = "Levar à loja"
    }
    conditional {
      if ($input.entrega_modo == "motoboy") {
        precondition ($input.coleta_endereco != null && $input.coleta_endereco != "") {
          error_type = "inputerror"
          error = "Informe o endereço de coleta para o motoboy."
        }
        precondition (($input.coleta_endereco|strlen) <= 200) {
          error_type = "inputerror"
          error = "O endereço de coleta deve ter no máximo 200 caracteres."
        }
        precondition (["Manhã", "Tarde", "Noite"]|in:$input.coleta_periodo) {
          error_type = "inputerror"
          error = "Escolha o período da coleta: Manhã, Tarde, Noite."
        }
        var.update $endereco {
          value = $input.coleta_endereco
        }
        var.update $periodo {
          value = $input.coleta_periodo
        }
        var.update $entrega {
          value = "Coleta por motoboy"
        }
      }
    }
    function.run "atech_autor" {
      input = {user_id: $auth.id}
    } as $autor
    db.transaction {
      stack {
        db.add "os_servicos" {
          data = {
            cliente_id: $eu.cliente_id,
            item_cliente_id: $aparelho.id,
            descricao_problema: $input.descricao_problema,
            status: "solicitado",
            atualizado_em: now,
            entrega_modo: $input.entrega_modo,
            coleta_endereco: $endereco,
            coleta_periodo: $periodo
          }
        } as $ordem
        db.add "os_historico" {
          data = {
            os_servicos_id: $ordem.id,
            autor: $autor,
            tipo: "Abertura",
            descricao: "Atendimento solicitado pelo cliente (" ~ $entrega ~ "). Problema relatado: " ~ $input.descricao_problema,
            para_status: ""
          }
        } as $evento
      }
    }
  }
  response = $ordem
  guid = "qWT_edIvt1NlK3RS6Y8bXQxbTe4"
}
