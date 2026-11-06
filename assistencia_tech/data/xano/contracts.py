"""Registro de contratos documentados da API do Xano.

REGRA: só adicione uma entrada aqui a partir da documentação oficial do
workspace Xano (Swagger/OpenAPI do API group), registrando a origem em
``source``. Nenhum endpoint, método ou campo pode ser deduzido ou inventado.

Enquanto o registro estiver vazio, toda operação no modo Xano falha com
``ContractPendingError`` sem enviar requisições.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from ..errors import ContractPendingError

# Operações internas que a aplicação precisa. Os nomes são internos e não
# correspondem a endpoints do Xano.
OPERATIONS: dict[str, str] = {
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
    "technicians.list": "listar técnicos",
    "orders.list": "listar ordens de serviço",
    "orders.get_by_code": "consultar ordem de serviço",
    "orders.next_code": "gerar o código da ordem de serviço",
    "orders.create": "abrir ordens de serviço",
    "orders.save": "atualizar a ordem de serviço",
    "auth.login": "entrar no sistema",
    "auth.register": "criar contas de acesso",
    "auth.me": "consultar a conta do usuário",
}


@dataclass(frozen=True)
class EndpointContract:
    method: str
    path: str
    source: str  # referência à documentação oficial (ex.: seção do Swagger)


# Vazio até a documentação oficial ser fornecida.
CONTRACTS: dict[str, EndpointContract] = {}


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
