// Confere se a ordem original admite ordem em garantia: entregue depois de concluída,
// há no máximo 90 dias, e do mesmo cliente e aparelho (add-deadlines-and-warranty).
function "atech_garantia_valida" {
  input {
    int os_servicos_id
    int cliente_id
    int item_cliente_id
  }
  stack {
    db.get "os_servicos" {
      field_name = "id"
      field_value = $input.os_servicos_id
    } as $original
    precondition ($original != null) {
      error_type = "notfound"
      error = "Ordem original não encontrada."
    }
    precondition ($original.status == "entregue") {
      error_type = "inputerror"
      error = "Só ordens concluídas e entregues têm garantia."
    }
    precondition ($original.cliente_id == $input.cliente_id && $original.item_cliente_id == $input.item_cliente_id) {
      error_type = "inputerror"
      error = "A ordem em garantia deve ser do mesmo cliente e equipamento da ordem original."
    }
    db.query "os_historico" {
      where = $db.os_historico.os_servicos_id == $original.id && $db.os_historico.para_status == "Concluído"
      return = {type: "exists"}
    } as $concluida
    precondition ($concluida) {
      error_type = "inputerror"
      error = "Só ordens concluídas e entregues têm garantia."
    }
    db.query "os_historico" {
      where = $db.os_historico.os_servicos_id == $original.id && $db.os_historico.para_status == "Entregue"
      sort = {created_at: "desc"}
      return = {type: "single"}
    } as $entrega
    precondition ($entrega != null && ($entrega.created_at|transform_timestamp:"+90 days") >= now) {
      error_type = "inputerror"
      error = "A garantia da ordem original terminou."
    }
  }
  response = $original.id
  guid = "yOclPBdtyfdzlTCH4ODJNmjUuIA"
}
