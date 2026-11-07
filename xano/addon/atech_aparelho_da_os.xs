addon atech_aparelho_da_os {
  input {
    int item_cliente_id
  }
  stack {
    db.query item_cliente {
      where = $db.item_cliente.id == $input.item_cliente_id
      return = {type: "single"}
    }
  }
  guid = "2SdWT2sSHAtSmOq4IFFrLrG3iwE"
}
