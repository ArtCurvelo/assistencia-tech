"""Registro de contratos documentados da API do Xano.

REGRA: só adicione uma entrada aqui a partir da documentação oficial do
workspace Xano (Swagger/OpenAPI do API group), registrando a origem em
``source``. Nenhum endpoint, método ou campo pode ser deduzido ou inventado.

Os contratos abaixo são os do backend em XanoScript da pasta ``xano/``
(workspace 170741), conferidos com ``python -m tools.xano_contract_check``
contra a documentação publicada (``/apispec:{grupo}``). Uma operação sem
contrato falha com ``ContractPendingError`` sem enviar requisições.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from ..errors import ContractPendingError

# Grupos lógicos; o identificador real de cada grupo vem da configuração.
GROUP_AUTH = "auth"
GROUP_CLIENTE = "cliente"
GROUP_OS = "os"

# Operações internas (nomes internos, não são endpoints do Xano).
OPERATIONS: dict[str, str] = {
    "auth.login": "entrar no sistema",
    "auth.me": "consultar a conta do usuário",
    "auth.signup_client": "criar a conta de cliente",
    "users.list": "listar colaboradores",
    "users.create": "cadastrar colaboradores",
    "users.update": "atualizar colaboradores",
    "technicians.list": "listar técnicos",
    "clients.list": "listar clientes",
    "clients.get": "consultar cliente",
    "clients.create": "cadastrar clientes",
    "clients.update": "editar clientes",
    "clients.delete": "excluir clientes",
    "equipment.list": "listar equipamentos",
    "equipment.get": "consultar equipamento",
    "equipment.create": "cadastrar equipamentos",
    "equipment.update": "editar equipamentos",
    "equipment.delete": "excluir equipamentos",
    "orders.list": "listar ordens de serviço",
    "orders.get": "consultar ordem de serviço",
    "orders.create": "abrir ordens de serviço",
    "orders.update": "atualizar a ordem de serviço",
    "orders.items.add": "adicionar itens ao orçamento",
    "orders.items.remove": "remover itens do orçamento",
    "orders.history.add": "registrar o histórico da ordem",
    "orders.payments.add": "registrar pagamentos",
    "portal.public_order": "consultar o status público da ordem",
    "portal.client_orders": "listar as ordens do cliente",
    "portal.client_account": "consultar o cadastro do cliente",
    "portal.client_decision": "registrar a decisão do cliente sobre o orçamento",
    "portal.client_rating": "registrar a avaliação do atendimento",
    "parts.list": "listar as peças do estoque",
    "parts.create": "cadastrar peças",
    "parts.update": "editar peças",
    "parts.restock": "registrar entradas de estoque",
    "parts.movements": "consultar as movimentações de estoque",
}


@dataclass(frozen=True)
class EndpointContract:
    method: str
    group: str  # grupo lógico (GROUP_AUTH, GROUP_CLIENTE, GROUP_OS)
    path: str  # caminho com marcadores no formato do Xano, ex.: /cliente/{cliente_id}
    source: str  # referência à documentação oficial
    public: bool = False  # True: sem token (login, cadastro e consulta pública)


def _c(method: str, group: str, path: str, *, public: bool = False) -> EndpointContract:
    return EndpointContract(method, group, path, f"apispec:{group} {method} {path}", public)


CONTRACTS: dict[str, EndpointContract] = {
    "auth.login": _c("POST", GROUP_AUTH, "/auth/login", public=True),
    "auth.me": _c("GET", GROUP_AUTH, "/auth/me"),
    "auth.signup_client": _c("POST", GROUP_AUTH, "/auth/signup_cliente", public=True),
    "users.list": _c("GET", GROUP_AUTH, "/usuarios"),
    "users.create": _c("POST", GROUP_AUTH, "/usuarios"),
    "users.update": _c("PATCH", GROUP_AUTH, "/usuarios/{user_id}"),
    "technicians.list": _c("GET", GROUP_AUTH, "/tecnicos"),
    "clients.list": _c("GET", GROUP_CLIENTE, "/cliente"),
    "clients.get": _c("GET", GROUP_CLIENTE, "/cliente/{cliente_id}"),
    "clients.create": _c("POST", GROUP_CLIENTE, "/cliente"),
    "clients.update": _c("PATCH", GROUP_CLIENTE, "/cliente/{cliente_id}"),
    "clients.delete": _c("DELETE", GROUP_CLIENTE, "/cliente/{cliente_id}"),
    "equipment.list": _c("GET", GROUP_CLIENTE, "/item_cliente"),
    "equipment.get": _c("GET", GROUP_CLIENTE, "/item_cliente/{item_cliente_id}"),
    "equipment.create": _c("POST", GROUP_CLIENTE, "/item_cliente"),
    "equipment.update": _c("PATCH", GROUP_CLIENTE, "/item_cliente/{item_cliente_id}"),
    "equipment.delete": _c("DELETE", GROUP_CLIENTE, "/item_cliente/{item_cliente_id}"),
    "orders.list": _c("GET", GROUP_OS, "/os_servicos"),
    "orders.get": _c("GET", GROUP_OS, "/os_servicos/{os_servicos_id}"),
    "orders.create": _c("POST", GROUP_OS, "/os_servicos"),
    "orders.update": _c("PATCH", GROUP_OS, "/os_servicos/{os_servicos_id}"),
    "orders.items.add": _c("POST", GROUP_OS, "/os_itens"),
    "orders.items.remove": _c("DELETE", GROUP_OS, "/os_itens/{os_itens_id}"),
    "orders.history.add": _c("POST", GROUP_OS, "/os_historico"),
    "orders.payments.add": _c("POST", GROUP_OS, "/pagamentos"),
    "portal.public_order": _c("GET", GROUP_OS, "/consulta_publica/{os_servicos_id}", public=True),
    "portal.client_orders": _c("GET", GROUP_OS, "/portal/minhas_ordens"),
    "portal.client_account": _c("GET", GROUP_OS, "/portal/minha_conta"),
    "portal.client_decision": _c("POST", GROUP_OS, "/portal/decisao_orcamento"),
    "portal.client_rating": _c("POST", GROUP_OS, "/portal/avaliacao"),
    "parts.list": _c("GET", GROUP_OS, "/pecas"),
    "parts.create": _c("POST", GROUP_OS, "/pecas"),
    "parts.update": _c("PATCH", GROUP_OS, "/pecas/{peca_id}"),
    "parts.restock": _c("POST", GROUP_OS, "/estoque/entrada"),
    "parts.movements": _c("GET", GROUP_OS, "/estoque/movimentos"),
}


def require_contract(
    operation: str,
    registry: Mapping[str, EndpointContract] | None = None,
) -> EndpointContract:
    """Retorna o contrato da operação ou lança ``ContractPendingError``."""
    if operation not in OPERATIONS:
        raise KeyError(f"Operação interna desconhecida: {operation}")
    contract = (CONTRACTS if registry is None else registry).get(operation)
    if contract is None:
        action = OPERATIONS[operation]
        raise ContractPendingError(
            f"A integração com o Xano para {action} ainda não está disponível: "
            "aguardando a documentação oficial da API.",
            detail=f"sem contrato registrado para '{operation}'",
        )
    return contract
