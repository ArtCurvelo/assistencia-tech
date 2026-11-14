query "portal/excluir_conta" verb=POST {
  api_group = "atech_os"
  description = "Perfil cliente (LGPD): confirma a senha, recusa se houver ordem em andamento, anonimiza o cadastro, desativa o login e apaga os comentários das avaliações; mantém as ordens (add-lgpd-portal)."
  auth = "user"
  input {
    text senha {
      sensitive = true
    }
  }
  stack {
    function.run "atech_usuario_autorizado" {
      input = {user_id: $auth.id, roles: ["cliente"]}
    } as $eu
    precondition ($eu.cliente_id != null) {
      error_type = "accessdenied"
      error = "Sua conta não está vinculada a um cadastro de cliente."
    }
    db.get "user" {
      field_name = "id"
      field_value = $auth.id
    } as $conta
    security.check_password {
      text_password = $input.senha
      hash_password = $conta.password
    } as $senha_ok
    precondition ($senha_ok) {
      error_type = "accessdenied"
      error = "Senha incorreta."
    }
    db.query "os_servicos" {
      where = $db.os_servicos.cliente_id == $eu.cliente_id && $db.os_servicos.status != "entregue" && $db.os_servicos.status != "cancelado"
      return = {type: "count"}
    } as $em_andamento
    precondition ($em_andamento == 0) {
      error_type = "inputerror"
      error = "Você tem ordens em andamento. A exclusão fica disponível depois que todas forem entregues ou canceladas."
    }
    db.query "avaliacao" {
      where = $db.avaliacao.cliente_id == $eu.cliente_id
      return = {type: "list"}
    } as $avaliacoes
    var $marcador {
      value = "anonimizado-" ~ $eu.cliente_id
    }
    db.transaction {
      stack {
        db.patch "cliente" {
          field_name = "id"
          field_value = $eu.cliente_id
          data = {
            Nome: "Cliente anonimizado",
            Cpf: $marcador,
            email: $marcador ~ "@removido.invalid",
            telefone_Aparelho: "",
            anonimizado: true
          }
        } as $cliente
        db.patch "user" {
          field_name = "id"
          field_value = $auth.id
          data = {
            name: "Cliente anonimizado",
            email: "anonimizado-u" ~ $auth.id ~ "@removido.invalid",
            ativo: false
          }
        } as $conta_anonimizada
        foreach ($avaliacoes) {
          each as $avaliacao {
            db.patch "avaliacao" {
              field_name = "id"
              field_value = $avaliacao.id
              data = {comentario: null}
            } as $sem_comentario
          }
        }
      }
    }
  }
  response = {anonimizado: true}
  guid = "qvk80iA34c2lwZXt6IPuyQ-zmug"
}
