"""Contrato-alvo que o backend Xano deve oferecer para a integração (opção A).

Este arquivo descreve o que a APLICAÇÃO precisa; ele não afirma que os
endpoints existem. O verificador (``xano_contract_check.py``) compara este
alvo com a documentação OpenAPI publicada pelo Xano e lista o que falta.
Somente depois de o verificador passar os contratos serão registrados em
``assistencia_tech/data/xano/contracts.py``.

Convenções:
- ``auth``: "public" (sem token), "bearer" (exige ``bearerAuth``).
- ``request``: campos que o corpo (ou a query, para GET) deve aceitar.
- ``response``: campos que a resposta 200 deve documentar. Para listas, os
  campos de cada item. ``None`` significa "resposta sem corpo relevante".
"""

from __future__ import annotations

from dataclasses import dataclass, field

ORDER_STATUS_VALUES = (
    "recebido",
    "em_analise",
    "aguardando_aprovacao",
    "em_reparo",
    "concluido",
    "entregue",
    "cancelado",
)
ROLE_VALUES = ("admin", "atendente", "tecnico", "cliente")

USER_FIELDS = ("id", "name", "email", "role", "cliente_id", "especialidade", "ativo")
CLIENT_FIELDS = ("id", "created_at", "Nome", "Cpf", "email", "telefone_Aparelho")
DEVICE_FIELDS = ("id", "cliente_id", "aparelho", "marca", "modelo", "numero_serie", "observacoes")
ITEM_FIELDS = ("id", "os_servicos_id", "tipo", "descricao", "quantidade", "valor_unitario")
PAYMENT_FIELDS = ("id", "os_servicos_id", "valor_a_ser_pago", "forma_de_pagamento", "data_do_pagamento")
EVENT_FIELDS = ("id", "os_servicos_id", "created_at", "autor", "tipo", "descricao", "para_status")
ORDER_FIELDS = (
    "id",
    "created_at",
    "atualizado_em",
    "cliente_id",
    "item_cliente_id",
    "user_id",
    "descricao_problema",
    "diagnostico",
    "motivo_cancelamento",
    "status",
)
ORDER_WITH_ADDONS = ORDER_FIELDS + ("_itens", "_pagamentos", "_historico")


@dataclass(frozen=True)
class Endpoint:
    method: str
    path: str
    auth: str
    request: tuple[str, ...] = ()
    response: tuple[str, ...] | None = ()
    enums: dict[str, tuple[str, ...]] = field(default_factory=dict)
    purpose: str = ""


# Grupos lógicos do contrato. Os códigos reais (api:XXXX) dependem da instância
# e são informados ao verificador; os padrões abaixo são os do workspace do grupo.
AUTH = "auth"
CLIENTE = "cliente"
OS = "os"

GROUP_TITLES = {AUTH: "Autenticação", CLIENTE: "Cliente", OS: "Ordens de Serviço"}
DEFAULT_INSTANCE = "https://x8ki-letl-twmt.n7.xano.io"
DEFAULT_GROUP_IDS = {AUTH: "GRUPO-AUTH-COLEGA", CLIENTE: "GRUPO-CLIENTE-COLEGA", OS: "GRUPO-OS-COLEGA"}

TARGET: dict[str, tuple[Endpoint, ...]] = {
    AUTH: (
        Endpoint("post", "/auth/login", "public", ("email", "password"), ("authToken", "user_id"),
                 purpose="Login; deve recusar usuários com ativo = false."),
        Endpoint("get", "/auth/me", "bearer", (), USER_FIELDS, {"role": ROLE_VALUES},
                 purpose="Conta autenticada com perfil e vínculos."),
        Endpoint("post", "/auth/signup_cliente", "public",
                 ("Nome", "Cpf", "email", "telefone_Aparelho", "password"), ("authToken", "user_id"),
                 purpose="Cadastro público: cria cliente e usuário 'cliente' na mesma transação."),
        Endpoint("get", "/usuarios", "bearer", (), USER_FIELDS, {"role": ROLE_VALUES},
                 purpose="Somente admin: lista colaboradores e clientes (sem senha)."),
        Endpoint("post", "/usuarios", "bearer", ("name", "email", "password", "role", "especialidade"), USER_FIELDS,
                 purpose="Somente admin: cria colaborador."),
        Endpoint("patch", "/usuarios/{user_id}", "bearer", ("name", "role", "especialidade", "ativo", "password"),
                 USER_FIELDS, purpose="Somente admin: edita, ativa/desativa ou redefine a senha."),
        Endpoint("get", "/tecnicos", "bearer", (), ("id", "name", "especialidade", "ativo"),
                 purpose="Colaboradores: técnicos para atribuição e histórico."),
    ),
    CLIENTE: (
        Endpoint("get", "/cliente", "bearer", ("busca", "page", "per_page"), ("items",),
                 purpose="Colaboradores: lista paginada; cada item com os campos do cliente."),
        Endpoint("post", "/cliente", "bearer", ("Nome", "Cpf", "email", "telefone_Aparelho"), CLIENT_FIELDS,
                 purpose="Cadastro no balcão; 400 para CPF ou e-mail duplicado."),
        Endpoint("get", "/cliente/{cliente_id}", "bearer", (), CLIENT_FIELDS),
        Endpoint("patch", "/cliente/{cliente_id}", "bearer", ("Nome", "Cpf", "email", "telefone_Aparelho"),
                 CLIENT_FIELDS),
        Endpoint("delete", "/cliente/{cliente_id}", "bearer", (), None, purpose="Somente admin."),
        Endpoint("get", "/item_cliente", "bearer", (), DEVICE_FIELDS),
        Endpoint("post", "/item_cliente", "bearer",
                 ("cliente_id", "aparelho", "marca", "modelo", "numero_serie", "observacoes"), DEVICE_FIELDS),
        Endpoint("get", "/item_cliente/{item_cliente_id}", "bearer", (), DEVICE_FIELDS),
        Endpoint("patch", "/item_cliente/{item_cliente_id}", "bearer",
                 ("cliente_id", "aparelho", "marca", "modelo", "numero_serie", "observacoes"), DEVICE_FIELDS),
        Endpoint("delete", "/item_cliente/{item_cliente_id}", "bearer", (), None, purpose="Somente admin."),
    ),
    OS: (
        Endpoint("get", "/os_servicos", "bearer", (), ORDER_WITH_ADDONS, {"status": ORDER_STATUS_VALUES},
                 purpose="Colaboradores: todas as ordens com itens, pagamentos e histórico."),
        Endpoint("get", "/os_servicos/{os_servicos_id}", "bearer", (), ORDER_WITH_ADDONS,
                 {"status": ORDER_STATUS_VALUES}),
        Endpoint("post", "/os_servicos", "bearer", ("cliente_id", "item_cliente_id", "descricao_problema", "status"),
                 ORDER_FIELDS, {"status": ORDER_STATUS_VALUES}),
        Endpoint("patch", "/os_servicos/{os_servicos_id}", "bearer",
                 ("status", "user_id", "diagnostico", "motivo_cancelamento", "atualizado_em"), ORDER_FIELDS,
                 {"status": ORDER_STATUS_VALUES}),
        Endpoint("post", "/os_itens", "bearer", ("os_servicos_id", "tipo", "descricao", "quantidade", "valor_unitario"),
                 ITEM_FIELDS, {"tipo": ("servico", "peca")}),
        Endpoint("delete", "/os_itens/{os_itens_id}", "bearer", (), None),
        Endpoint("post", "/os_historico", "bearer",
                 ("os_servicos_id", "autor", "tipo", "descricao", "para_status"), EVENT_FIELDS),
        Endpoint("post", "/pagamentos", "bearer",
                 ("os_servicos_id", "valor_a_ser_pago", "forma_de_pagamento", "data_do_pagamento"), PAYMENT_FIELDS),
        Endpoint("get", "/consulta_publica/{os_servicos_id}", "public", (),
                 ("id", "status", "aparelho", "modelo", "atualizado_em"), {"status": ORDER_STATUS_VALUES},
                 purpose="Consulta pública: somente estes campos, sem dados pessoais nem valores."),
        Endpoint("get", "/portal/minhas_ordens", "bearer", (), ORDER_WITH_ADDONS, {"status": ORDER_STATUS_VALUES},
                 purpose="Perfil cliente: somente as ordens do cliente vinculado ao token."),
    ),
}
