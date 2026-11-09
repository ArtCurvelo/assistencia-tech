query "estatisticas_publicas" verb=GET {
  api_group = "atech_os"
  description = "Público: somente contagens agregadas para a página inicial (entregues, em atendimento, avaliações, promotores e detratores); sem dados pessoais, valores ou códigos (add-public-stats)."
  input {}
  stack {
    db.query "os_servicos" {
      where = $db.os_servicos.status == "entregue"
      return = {type: "count"}
    } as $entregues
    db.query "os_servicos" {
      where = $db.os_servicos.status != "entregue" && $db.os_servicos.status != "cancelado"
      return = {type: "count"}
    } as $em_atendimento
    db.query "avaliacao" {
      return = {type: "count"}
    } as $avaliacoes
    db.query "avaliacao" {
      where = $db.avaliacao.nota >= 9
      return = {type: "count"}
    } as $promotores
    db.query "avaliacao" {
      where = $db.avaliacao.nota <= 6
      return = {type: "count"}
    } as $detratores
  }
  response = {
    entregues: $entregues,
    em_atendimento: $em_atendimento,
    avaliacoes: $avaliacoes,
    promotores: $promotores,
    detratores: $detratores
  }
  guid = "kVIhP6VKprIH_XaUefaP3z2EdjY"
}
