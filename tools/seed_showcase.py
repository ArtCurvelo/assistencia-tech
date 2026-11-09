"""Povoa o backend com dados fictícios de vitrine, pelas regras do próprio sistema.

Cada registro passa pelos serviços da aplicação (validações, histórico, baixa no
estoque, pagamentos, decisões e avaliações dos clientes), como num uso real.
Nenhuma credencial fica no código: as senhas dos colaboradores vêm de um arquivo
local (``email senha`` por linha) e as senhas geradas para os clientes de teste
são gravadas em outro arquivo local, ambos fora do repositório.

Uso:
    python -m tools.seed_showcase --demo                       # ensaio no modo demonstração
    python -m tools.seed_showcase --xano --colaboradores ARQ --saida-clientes ARQ2

Dados fictícios: nomes inventados, CPFs gerados com dígitos válidos e e-mails
no domínio reservado ``exemplo.test``.
"""

from __future__ import annotations

import argparse
import asyncio
import pathlib
import random
import secrets
import string
import sys
from dataclasses import dataclass, field

from assistencia_tech.config import Settings
from assistencia_tech.data.demo import build_demo_gateway
from assistencia_tech.data.demo.users import DEMO_PASSWORDS
from assistencia_tech.data.factory import build_gateway
from assistencia_tech.data.request_context import current_backend_token, use_backend_token
from assistencia_tech.services import (
    AuthService,
    ClientService,
    EquipmentService,
    InventoryService,
    OrderService,
    PortalService,
)

XANO_BASE_URL = "https://x8ki-letl-twmt.n7.xano.io"
DOMAIN = "exemplo.test"

# ----------------------------------------------------------------------
# Dados fictícios
# ----------------------------------------------------------------------
# (nome, tem conta no portal)
CLIENTS = [
    ("Larissa Moura", True), ("Thiago Barros", True), ("Fernanda Quintela", True),
    ("Eduardo Prates", True), ("Juliana Siqueira", True), ("Rodrigo Azevedo", True),
    ("Patrícia Lemos", False), ("Gustavo Rangel", False), ("Aline Furtado", False),
    ("Marcelo Toledo", False), ("Bianca Correia", False), ("Henrique Valadares", False),
]

# (índice do cliente, tipo, marca, modelo, número de série)
EQUIPMENT = [
    (0, "Notebook", "Dell", "Inspiron 15 3520", "DL3520-4471"),
    (1, "Console", "Sony", "PlayStation 5", "PS5-CFI-1215"),
    (2, "Celular", "Samsung", "Galaxy S23", "SM-S911-0832"),
    (3, "Computador", "Lenovo", "ThinkCentre M70s", "LNV-M70S-2290"),
    (4, "Notebook", "Acer", "Nitro 5", "ACN5-77812"),
    (5, "Tablet", "Apple", "iPad Air 5", "IPA5-30129"),
    (6, "Celular", "Motorola", "Moto G54", ""),
    (7, "Console", "Microsoft", "Xbox Series X", "XSX-664301"),
    (8, "Notebook", "Asus", "VivoBook 15", "ASV15-11902"),
    (9, "Computador", "HP", "ProDesk 400 G7", "HP400-55871"),
    (10, "Celular", "Xiaomi", "Redmi Note 13", ""),
    (11, "Console", "Nintendo", "Switch OLED", "NSW-OLED-7731"),
    (0, "Celular", "Apple", "iPhone 13", "IP13-90214"),
    (2, "Notebook", "Samsung", "Galaxy Book2", "SGB2-31187"),
    (6, "Computador", "Positivo", "Master D610", "POS-D610-0076"),
]

# (código, nome, preço de venda, estoque mínimo, entrada inicial)
PARTS = [
    ("SSD-480-NV", "SSD NVMe 480 GB", "289,90", 2, 6),
    ("RAM-8-DDR4", "Memória DDR4 8 GB", "179,90", 2, 8),
    ("PASTA-TERM", "Pasta térmica prata", "34,90", 3, 12),
    ("FONTE-500", "Fonte ATX 500 W 80 Plus", "329,00", 1, 3),
    ("TELA-S23", "Tela AMOLED Galaxy S23", "899,00", 1, 2),
    ("BAT-G54", "Bateria Moto G54", "149,90", 2, 4),
    ("CON-USBC", "Conector de carga USB-C", "45,00", 3, 10),
    ("COOLER-NB", "Cooler para notebook", "119,90", 2, 4),
    ("CTRL-ANALOG", "Analógico para controle", "59,90", 2, 6),
    ("TECL-NB15", "Teclado para notebook 15\"", "189,90", 1, 2),
]

SVC, PART = "Serviço", "Peça"


@dataclass
class OrderPlan:
    client: int
    equipment: int
    problem: str
    technician: int  # índice na lista de técnicos (módulo a quantidade)
    stage: str  # recebido, analise, aguardando, reparo, concluido, entregue, recusado, cancelado
    diagnosis: str = ""
    items: list[tuple] = field(default_factory=list)  # (tipo, descrição, qtd, preço, código da peça ou "")
    payment: str = "PIX"
    rating: tuple[int, str] | None = None


ORDERS = [
    OrderPlan(0, 0, "Notebook muito lento e esquentando", 0, "entregue",
              "Disco rígido com setores defeituosos e cooler obstruído.",
              [(SVC, "Instalação de SSD e migração do sistema", 1, "150,00", ""),
               (PART, "SSD NVMe 480 GB", 1, "", "SSD-480-NV"), (SVC, "Limpeza interna", 1, "80,00", "")],
              "Cartão de crédito", (10, "Ficou muito mais rápido, atendimento excelente!")),
    OrderPlan(1, 1, "Console desliga sozinho durante os jogos", 1, "entregue",
              "Superaquecimento por pasta térmica ressecada.",
              [(SVC, "Limpeza interna e troca de pasta térmica", 1, "180,00", ""),
               (PART, "Pasta térmica prata", 1, "", "PASTA-TERM")],
              "PIX", (9, "Resolveram rápido e explicaram o problema.")),
    OrderPlan(2, 2, "Tela trincada após queda", 2, "entregue",
              "Display AMOLED danificado; touch sem resposta na parte inferior.",
              [(SVC, "Troca de tela", 1, "150,00", ""), (PART, "Tela AMOLED Galaxy S23", 1, "", "TELA-S23")],
              "Cartão de débito", (8, "Bom serviço, mas demorou um pouco mais que o previsto.")),
    OrderPlan(3, 3, "Computador não liga", 0, "entregue",
              "Fonte de alimentação queimada; demais componentes testados e funcionando.",
              [(SVC, "Substituição da fonte", 1, "90,00", ""), (PART, "Fonte ATX 500 W 80 Plus", 1, "", "FONTE-500")],
              "Dinheiro", (6, "Funcionou, mas achei o preço alto.")),
    OrderPlan(4, 4, "Teclado com várias teclas falhando", 1, "entregue",
              "Teclado danificado por líquido.",
              [(SVC, "Troca do teclado", 1, "90,00", ""), (PART, "Teclado para notebook 15\"", 1, "", "TECL-NB15")],
              "PIX", (10, "Notebook voltou perfeito. Recomendo!")),
    OrderPlan(7, 7, "Controle com analógico puxando para o lado", 2, "entregue",
              "Analógico esquerdo com desgaste (drift).",
              [(SVC, "Troca de analógico", 1, "60,00", ""), (PART, "Analógico para controle", 1, "", "CTRL-ANALOG")],
              "Dinheiro"),
    OrderPlan(8, 8, "Notebook não carrega a bateria", 0, "concluido",
              "Conector de carga solto da placa.",
              [(SVC, "Troca do conector de carga", 1, "120,00", ""),
               (PART, "Conector de carga USB-C", 1, "", "CON-USBC")]),
    OrderPlan(9, 9, "Computador reiniciando e travando", 1, "concluido",
              "Pente de memória com defeito.",
              [(SVC, "Diagnóstico e troca de memória", 1, "70,00", ""), (PART, "Memória DDR4 8 GB", 1, "", "RAM-8-DDR4")]),
    OrderPlan(5, 5, "Tablet não conecta ao Wi-Fi", 2, "reparo",
              "Falha no módulo de rede; necessária reinstalação do sistema e recalibração.",
              [(SVC, "Restauração do sistema e recalibração de rede", 1, "160,00", "")]),
    OrderPlan(10, 10, "Celular com bateria estufada", 0, "reparo",
              "Bateria estufada pressionando a tela.",
              [(SVC, "Troca de bateria", 1, "70,00", ""), (PART, "Bateria Moto G54", 1, "", "BAT-G54")]),
    OrderPlan(11, 11, "Switch não lê cartuchos", 1, "reparo",
              "Leitor de cartão de jogo com contatos oxidados.",
              [(SVC, "Limpeza e reparo do leitor de cartuchos", 1, "140,00", "")]),
    OrderPlan(0, 12, "iPhone com Face ID parado", 2, "aguardando",
              "Módulo de câmera frontal com falha; Face ID indisponível.",
              [(SVC, "Reparo do módulo do Face ID", 1, "480,00", "")]),
    OrderPlan(2, 13, "Notebook superaquecendo e desligando", 0, "aguardando",
              "Cooler com rolamento travado.",
              [(SVC, "Troca do cooler e limpeza", 1, "90,00", ""), (PART, "Cooler para notebook", 1, "", "COOLER-NB")]),
    OrderPlan(6, 6, "Celular não reconhece o chip", 1, "aguardando",
              "Gaveta do chip danificada e leitor com contatos dobrados.",
              [(SVC, "Troca do leitor de chip", 1, "130,00", "")]),
    OrderPlan(3, 3, "Computador com barulho alto", 2, "analise"),
    OrderPlan(6, 14, "Computador sem imagem no monitor", 0, "analise"),
    OrderPlan(7, 7, "Xbox não liga após queda de energia", 1, "recebido"),
    OrderPlan(9, 9, "Instalação de SSD adicional", 2, "recebido"),
    OrderPlan(5, 5, "Tela do tablet com manchas", 0, "recusado",
              "Painel LCD com manchas; troca do conjunto necessária.",
              [(SVC, "Troca do conjunto de tela", 1, "950,00", "")]),
    OrderPlan(10, 10, "Celular caiu na água", 1, "cancelado"),
]

STAGE_FLOW = ["Em análise", "Aguardando aprovação", "Em reparo", "Concluído", "Entregue"]
STAGE_DEPTH = {"recebido": 0, "analise": 1, "aguardando": 2, "reparo": 3, "concluido": 4, "entregue": 5,
               "recusado": 2, "cancelado": 0}


# ----------------------------------------------------------------------
# Apoio
# ----------------------------------------------------------------------
def cpf(rng: random.Random) -> str:
    digits = [rng.randint(0, 9) for _ in range(9)]
    while len(set(digits)) == 1:
        digits = [rng.randint(0, 9) for _ in range(9)]
    for size in (9, 10):
        total = sum(d * w for d, w in zip(digits, range(size + 1, 1, -1)))
        digits.append((total * 10 % 11) % 10)
    return "".join(map(str, digits))


def slug_email(name: str) -> str:
    import unicodedata

    plain = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    return ".".join(plain.split()) + f"@{DOMAIN}"


def strong_password() -> str:
    alphabet = string.ascii_letters + string.digits
    return "Vt" + "".join(secrets.choice(alphabet) for _ in range(14)) + "7a"


@dataclass
class Actor:
    token: str | None
    principal: object


class Seeder:
    def __init__(self, gateway, log=print):
        self.gw = gateway
        self.log = log
        self.rng = random.Random(20261109)

    def _as(self, actor: Actor):
        use_backend_token(actor.token)
        return actor.principal

    async def login(self, email: str, password: str) -> Actor:
        # login devolve o identificador da sessão do site; o JWT do Xano (None na demonstração)
        # fica no contexto da requisição logo após o login.
        _, principal = await AuthService(self.gw).login(email, password)
        return Actor(current_backend_token(), principal)

    async def run(self, attendant: Actor, technicians: list[Actor]) -> dict[str, str]:
        client_passwords: dict[str, str] = {}
        clients, client_actors, equipment, parts = [], {}, [], {}

        self.log("Peças e estoque…")
        stock = InventoryService(self.gw, self._as(attendant))
        existing = {p.code: p for p in await stock.list()}
        for code, name, price, minimum, quantity in PARTS:
            part = existing.get(code) or await stock.create(
                {"code": code, "name": name, "unit_price": price, "min_quantity": minimum})
            if part.quantity < quantity:
                part = await stock.restock(part.id, quantity - part.quantity, "Estoque inicial da vitrine")
            parts[code] = part

        self.log("Clientes…")
        for name, with_account in CLIENTS:
            email = slug_email(name)
            form = {"name": name, "cpf": cpf(self.rng), "email": email,
                    "phone": f"(11) 9{self.rng.randint(1000, 9999)}-{self.rng.randint(1000, 9999)}"}
            if with_account:
                password = strong_password()
                _, principal = await AuthService(self.gw).register_client(
                    {**form, "password": password, "password_confirm": password})
                client_passwords[email] = password
                client_actors[len(clients)] = Actor(current_backend_token(), principal)
                clients.append(principal.client_id)
            else:
                created = await ClientService(self.gw, self._as(attendant)).create(form)
                clients.append(created.id)

        self.log("Equipamentos…")
        for client_index, kind, brand, model, serial in EQUIPMENT:
            created = await EquipmentService(self.gw, self._as(attendant)).create(
                {"client_id": clients[client_index], "kind": kind, "brand": brand, "model": model,
                 "serial_number": serial, "notes": ""})
            equipment.append(created.id)

        self.log("Ordens de serviço…")
        for number, plan in enumerate(ORDERS, 1):
            code = await self._order(plan, attendant, technicians, clients, equipment, parts, client_actors)
            self.log(f"  {number:2}/{len(ORDERS)} {code} → {plan.stage}")
        use_backend_token(None)
        return client_passwords

    async def _order(self, plan, attendant, technicians, clients, equipment, parts, client_actors) -> str:
        tech = technicians[plan.technician % len(technicians)]
        staff = OrderService(self.gw, self._as(attendant))
        order = await staff.open({"client_id": clients[plan.client], "equipment_id": equipment[plan.equipment],
                                  "problem": plan.problem})
        code = order.code
        await OrderService(self.gw, self._as(attendant)).assign_technician(code, tech.principal.technician_id)
        if plan.stage == "cancelado":
            await OrderService(self.gw, self._as(attendant)).change_status(
                code, "Cancelado", "Cliente desistiu do reparo antes da análise.")
            return code
        depth = STAGE_DEPTH[plan.stage]
        if depth >= 1:
            await OrderService(self.gw, self._as(tech)).change_status(code, "Em análise")
        if depth >= 2:
            await OrderService(self.gw, self._as(tech)).record_diagnosis(code, plan.diagnosis)
            for kind, description, quantity, price, part_code in plan.items:
                form = {"kind": kind, "description": description, "quantity": str(quantity), "unit_price": price}
                if part_code:
                    form.update(part_id=parts[part_code].id, unit_price=str(parts[part_code].unit_price))
                await OrderService(self.gw, self._as(tech)).add_item(code, form)
            await OrderService(self.gw, self._as(tech)).change_status(code, "Aguardando aprovação")
        client = client_actors.get(plan.client)
        if plan.stage == "recusado":
            if client:
                await PortalService(self.gw, self._as(client)).decide_budget(
                    code, False, "O valor ficou acima do que posso pagar agora.")
            else:
                await OrderService(self.gw, self._as(attendant)).change_status(
                    code, "Cancelado", "Cliente não aprovou o orçamento.")
            return code
        if depth >= 3:
            if client:
                await PortalService(self.gw, self._as(client)).decide_budget(code, True, "")
            else:
                await OrderService(self.gw, self._as(attendant)).change_status(code, "Em reparo")
        if depth >= 4:
            await OrderService(self.gw, self._as(tech)).change_status(code, "Concluído")
        if depth >= 5:
            current = await OrderService(self.gw, self._as(attendant)).get(code)
            from assistencia_tech.domain.pricing import compute_totals

            balance = compute_totals(current).balance
            if balance > 0:
                await OrderService(self.gw, self._as(attendant)).add_payment(
                    code, {"amount": f"{balance:.2f}".replace(".", ","), "method": plan.payment})
            await OrderService(self.gw, self._as(attendant)).change_status(code, "Entregue")
            if plan.rating and client:
                score, comment = plan.rating
                await PortalService(self.gw, self._as(client)).rate(code, score, comment)
        return code


# ----------------------------------------------------------------------
# Execução
# ----------------------------------------------------------------------
def read_credentials(path: pathlib.Path) -> list[tuple[str, str]]:
    pairs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            email, password = line.split(maxsplit=1)
            pairs.append((email.strip(), password.strip()))
    return pairs


async def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--demo", action="store_true", help="ensaio no modo demonstração (memória)")
    target.add_argument("--xano", action="store_true", help="povoar o backend Xano")
    parser.add_argument("--colaboradores", type=pathlib.Path,
                        help="arquivo local com 'email senha' por linha: atendente primeiro, depois técnicos")
    parser.add_argument("--saida-clientes", type=pathlib.Path,
                        help="arquivo local onde gravar as senhas geradas para os clientes de teste")
    args = parser.parse_args(argv)

    if args.demo:
        gateway = build_demo_gateway()
        staff = [("atendimento@assistencia.test", DEMO_PASSWORDS["atendimento@assistencia.test"])]
        staff += [(e, DEMO_PASSWORDS[e]) for e in ("carlos@assistencia.test", "fernanda@assistencia.test",
                                                   "diego@assistencia.test")]
    else:
        if not args.colaboradores or not args.saida_clientes:
            parser.error("--xano exige --colaboradores e --saida-clientes")
        gateway = build_gateway(Settings(data_source="xano", xano_base_url=XANO_BASE_URL))
        staff = read_credentials(args.colaboradores)

    seeder = Seeder(gateway)
    attendant = await seeder.login(*staff[0])
    technicians = [await seeder.login(*pair) for pair in staff[1:]]
    if not technicians or any(not t.principal.technician_id for t in technicians):
        print("Informe ao menos um técnico após a atendente.", file=sys.stderr)
        return 2
    passwords = await seeder.run(attendant, technicians)
    if args.saida_clientes:
        args.saida_clientes.write_text("".join(f"{e} {p}\n" for e, p in passwords.items()), encoding="utf-8")
    print(f"Concluído: {len(CLIENTS)} clientes, {len(EQUIPMENT)} equipamentos, {len(PARTS)} peças, "
          f"{len(ORDERS)} ordens.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
