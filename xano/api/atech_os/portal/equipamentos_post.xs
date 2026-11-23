query "portal/equipamentos" verb=POST {
  api_group = "atech_os"
  description = "Perfil cliente: cadastra um aparelho no próprio cadastro; o cliente vem do token, nunca da requisição (add-client-self-service)."
  auth = "user"
  input {
    text aparelho filters=trim
    text marca filters=trim
    text modelo filters=trim
    text? numero_serie? filters=trim
    text? observacoes? filters=trim
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["cliente"]}
    } as $eu
    precondition ($eu.cliente_id != null) {
      error_type = "accessdenied"
      error = "Sua conta não está vinculada a um cadastro de cliente."
    }
    precondition (["Computador", "Notebook", "Console", "Celular", "Tablet", "Outro"]|in:$input.aparelho) {
      error_type = "inputerror"
      error = "Tipo inválido; use Computador, Notebook, Console, Celular, Tablet ou Outro."
    }
    precondition ($input.marca != "" && $input.modelo != "") {
      error_type = "inputerror"
      error = "Preencha a marca e o modelo do equipamento."
    }
    conditional {
      if ($input.numero_serie != null && $input.numero_serie != "") {
        db.query "item_cliente" {
          where = $db.item_cliente.numero_serie == $input.numero_serie
          return = {type: "exists"}
        } as $serie_em_uso
        precondition (!$serie_em_uso) {
          error_type = "inputerror"
          error = "Este número de série já está cadastrado."
        }
      }
    }
    db.add "item_cliente" {
      data = {
        cliente_id: $eu.cliente_id,
        aparelho: $input.aparelho,
        marca: $input.marca,
        modelo: $input.modelo,
        numero_serie: $input.numero_serie,
        observacoes: $input.observacoes
      }
    } as $aparelho
  }
  response = $aparelho
  guid = "ailsqRX_6HTAH90DvkiqsS_inoM"
}
