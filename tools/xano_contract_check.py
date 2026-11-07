"""Verifica se a documentação OpenAPI do Xano atende ao contrato-alvo.

Uso (na raiz do projeto, com a .venv ativa):

    python -m tools.xano_contract_check            # baixa a documentação atual do Xano
    python -m tools.xano_contract_check --offline  # usa as cópias em docs/xano-openapi/

    # Outra instância ou outros grupos (ou variáveis XANO_INSTANCE, XANO_GROUP_AUTH,
    # XANO_GROUP_CLIENTE e XANO_GROUP_OS):
    python -m tools.xano_contract_check --instance https://xxxx.xano.io --auth AAAA --cliente BBBB --os CCCC

Somente a documentação (``/apispec:<grupo>?type=json``) é lida; nenhum
endpoint de dados é chamado. A saída lista, por grupo, cada endpoint do
contrato-alvo como OK ou com as pendências encontradas.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
from collections.abc import Mapping
from typing import Any

import httpx

from assistencia_tech.data.xano.tls import system_ssl_context

from .xano_target_contract import DEFAULT_GROUP_IDS, DEFAULT_INSTANCE, GROUP_TITLES, TARGET, Endpoint

SNAPSHOTS = pathlib.Path(__file__).resolve().parent.parent / "docs" / "xano-openapi"


def _schema_fields(schema: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    if schema.get("type") == "array":
        schema = schema.get("items", {})
    return dict(schema.get("properties", {}))


def _request_fields(op: Mapping[str, Any]) -> set[str]:
    fields = {p.get("name", "") for p in op.get("parameters", []) if p.get("in") == "query"}
    for content in op.get("requestBody", {}).get("content", {}).values():
        fields |= set(_schema_fields(content.get("schema", {})))
    return fields


def _response_fields(op: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    for content in op.get("responses", {}).get("200", {}).get("content", {}).values():
        return _schema_fields(content.get("schema", {}))
    return {}


def check_endpoint(spec: Mapping[str, Any] | None, target: Endpoint) -> list[str]:
    """Lista de pendências (vazia quando o endpoint atende ao alvo)."""
    if spec is None:
        return ["documentação do grupo indisponível"]
    op = spec.get("paths", {}).get(target.path, {}).get(target.method)
    if op is None:
        return ["endpoint não existe"]
    problems: list[str] = []
    secured = bool(op.get("security") or spec.get("security"))
    if target.auth == "bearer" and not secured:
        problems.append("não exige autenticação (bearerAuth)")
    if target.auth == "public" and secured:
        problems.append("deveria ser público")
    missing_in = sorted(set(target.request) - _request_fields(op))
    if missing_in:
        problems.append("entrada sem: " + ", ".join(missing_in))
    if target.response is not None:
        fields = _response_fields(op)
        if not fields:
            problems.append("resposta sem esquema documentado")
        else:
            missing_out = [f for f in target.response if f not in fields]
            if missing_out:
                problems.append("resposta sem: " + ", ".join(missing_out))
            for name, values in target.enums.items():
                enum = tuple(fields.get(name, {}).get("enum", ()))
                if name in fields and set(enum) != set(values):
                    problems.append(f"{name} deve aceitar {', '.join(values)} (hoje: {', '.join(enum) or '—'})")
    return problems


def load_specs(
    offline: bool,
    instance: str = DEFAULT_INSTANCE,
    group_ids: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    ids = {**DEFAULT_GROUP_IDS, **(group_ids or {})}
    specs: dict[str, Any] = {}
    for group in TARGET:
        if offline:
            match = next(SNAPSHOTS.glob(f"*-{ids[group]}.json"), None)
            specs[group] = json.loads(match.read_text(encoding="utf-8")) if match else None
            continue
        try:
            response = httpx.get(
                f"{instance.rstrip('/')}/apispec:{ids[group]}",
                params={"type": "json"},
                timeout=30,
                verify=system_ssl_context(),
            )
            specs[group] = response.json() if response.status_code == 200 else None
        except (httpx.HTTPError, ValueError):
            specs[group] = None
    return specs


def report(specs: Mapping[str, Any], group_ids: Mapping[str, str] | None = None) -> tuple[str, int]:
    ids = {**DEFAULT_GROUP_IDS, **(group_ids or {})}
    lines, pending = [], 0
    for group, endpoints in TARGET.items():
        lines.append(f"\n== {GROUP_TITLES[group]} (api:{ids[group]})")
        for target in endpoints:
            problems = check_endpoint(specs.get(group), target)
            status = "OK " if not problems else "FALTA"
            lines.append(f"  [{status}] {target.method.upper():6} {target.path}")
            for problem in problems:
                lines.append(f"           - {problem}")
            pending += bool(problems)
    total = sum(len(e) for e in TARGET.values())
    lines.append(f"\nResultado: {total - pending} de {total} endpoints atendem ao contrato-alvo.")
    return "\n".join(lines), pending


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--offline", action="store_true", help="usar as cópias em docs/xano-openapi/")
    parser.add_argument("--instance", default=os.environ.get("XANO_INSTANCE", DEFAULT_INSTANCE),
                        help="endereço da instância Xano (ex.: https://xxxx.n7.xano.io)")
    for group in TARGET:
        parser.add_argument(f"--{group}", default=os.environ.get(f"XANO_GROUP_{group.upper()}"),
                            help=f"código do grupo {GROUP_TITLES[group]} (parte depois de 'api:')")
    args = parser.parse_args(argv)
    group_ids = {g: getattr(args, g) for g in TARGET if getattr(args, g)}
    text, pending = report(load_specs(args.offline, args.instance, group_ids), group_ids)
    print(text)
    return 1 if pending else 0


if __name__ == "__main__":
    sys.exit(main())
