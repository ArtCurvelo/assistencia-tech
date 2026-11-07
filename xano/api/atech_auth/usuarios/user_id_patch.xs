query "usuarios/{user_id}" verb=PATCH {
  api_group = "atech_auth"
  description = "Somente admin: edita nome, perfil, especialidade, situação ou senha."
  auth = "user"
  input {
    int user_id {
      table = "user"
    }
    text? name? filters=trim
    enum? role? {
      values = ["admin", "atendente", "tecnico", "cliente"]
    }
    text? especialidade? filters=trim
    bool? ativo?
    text? password? {
      sensitive = true
    }
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["admin"]}
    }
    db.get "user" {
      field_name = "id"
      field_value = $input.user_id
    } as $alvo
    precondition ($alvo != null) {
      error_type = "notfound"
      error = "Conta não encontrada."
    }
    var $updates {
      value = {}
    }
    conditional {
      if ($input.name != null) {
        var.update $updates.name {
          value = $input.name
        }
      }
    }
    conditional {
      if ($input.role != null) {
        var.update $updates.role {
          value = $input.role
        }
      }
    }
    conditional {
      if ($input.especialidade != null) {
        var.update $updates.especialidade {
          value = $input.especialidade
        }
      }
    }
    conditional {
      if ($input.ativo != null) {
        var.update $updates.ativo {
          value = $input.ativo
        }
      }
    }
    conditional {
      if ($input.password != null && $input.password != "") {
        precondition (($input.password|strlen) >= 8) {
          error_type = "inputerror"
          error = "A senha deve ter no mínimo 8 caracteres."
        }
        var.update $updates.password {
          value = $input.password
        }
      }
    }
    db.patch "user" {
      field_name = "id"
      field_value = $input.user_id
      data = $updates
    } as $atualizado
  }
  response = $atualizado|unset:"password"
  guid = "1d9Py6n1WT7UB0k4jo541KlHTfM"
}
