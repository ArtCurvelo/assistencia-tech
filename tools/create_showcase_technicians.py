"""Cria técnicos fictícios de vitrine no Xano, com a conta de administrador digitada no terminal.

Os nomes vêm de um gerador simples de pessoas fictícias; e-mails no domínio
reservado ``exemplo.test`` e senhas aleatórias. A senha do administrador é lida
com ``getpass`` (não aparece na tela nem fica em arquivo) e só serve para criar
as contas. As credenciais dos técnicos criados são gravadas no arquivo local
indicado, fora do repositório, para o roteiro ``tools.seed_showcase``.

Uso:
    python -m tools.create_showcase_technicians --saida ARQUIVO [--quantidade 2]
"""

from __future__ import annotations

import argparse
import asyncio
import getpass
import pathlib
import random
import secrets
import string
import sys
import unicodedata

from assistencia_tech.config import Settings
from assistencia_tech.data.errors import DataAccessError
from assistencia_tech.data.factory import build_gateway
from assistencia_tech.data.request_context import current_backend_token, use_backend_token
from assistencia_tech.services import AuthService, StaffService

XANO_BASE_URL = "https://x8ki-letl-twmt.n7.xano.io"
FIRST_NAMES = ["Rafael", "Juliana", "Bruno", "Camila", "Leonardo", "Mariana", "Diego", "Renata", "Felipe",
               "Tatiane", "Vinícius", "Priscila"]
LAST_NAMES = ["Costa", "Prado", "Nogueira", "Pacheco", "Ribas", "Teixeira", "Monteiro", "Andrade", "Carvalho",
              "Pimentel", "Duarte", "Fontes"]
SPECIALTIES = ["Computadores e notebooks", "Consoles e celulares", "Tablets e smartphones", "Placas e microsoldagem"]


def fictitious_people(count: int, rng: random.Random) -> list[tuple[str, str, str]]:
    names = set()
    while len(names) < count:
        names.add(f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}")
    people = []
    for index, name in enumerate(sorted(names)):
        plain = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
        people.append((name, ".".join(plain.split()) + "@exemplo.test", SPECIALTIES[index % len(SPECIALTIES)]))
    return people


def strong_password() -> str:
    alphabet = string.ascii_letters + string.digits
    return "Tc" + "".join(secrets.choice(alphabet) for _ in range(14)) + "9b"


async def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--saida", type=pathlib.Path, required=True, help="arquivo local para 'email senha'")
    parser.add_argument("--quantidade", type=int, default=2)
    args = parser.parse_args(argv)

    admin_email = input("E-mail do administrador: ").strip()
    admin_password = getpass.getpass("Senha do administrador (não aparece ao digitar): ")
    gateway = build_gateway(Settings(data_source="xano", xano_base_url=XANO_BASE_URL))
    try:
        # login devolve o identificador da sessão do site; o JWT do Xano fica no contexto da requisição.
        _, admin = await AuthService(gateway).login(admin_email, admin_password)
        token = current_backend_token()
    except DataAccessError as error:
        print(f"Não foi possível entrar: {error.user_message}", file=sys.stderr)
        return 1
    finally:
        del admin_password

    created = []
    for name, email, specialty in fictitious_people(args.quantidade, random.Random()):
        password = strong_password()
        use_backend_token(token)
        try:
            await StaffService(gateway, admin).create({"name": name, "email": email, "role": "Técnico",
                                                       "specialty": specialty, "password": password})
        except DataAccessError as error:
            print(f"  {name}: {error.user_message}", file=sys.stderr)
            continue
        created.append((email, password))
        print(f"  Técnico criado: {name} ({email}) — {specialty}")
    use_backend_token(None)
    with args.saida.open("a", encoding="utf-8") as out:
        out.writelines(f"{email} {password}\n" for email, password in created)
    print(f"{len(created)} técnico(s) criado(s). Credenciais gravadas em {args.saida}.")
    return 0 if created else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
