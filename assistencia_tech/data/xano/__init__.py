"""Adaptador do backend Xano."""

from .client import XanoClient, error_for_status
from .contracts import CONTRACTS, OPERATIONS, EndpointContract, require_contract
from .gateway import build_xano_gateway

__all__ = [
    "CONTRACTS",
    "OPERATIONS",
    "EndpointContract",
    "XanoClient",
    "build_xano_gateway",
    "error_for_status",
    "require_contract",
]
