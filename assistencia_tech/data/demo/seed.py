"""Dados fictícios do modo demonstração.

Todos os nomes, CPFs, e-mails e telefones são fictícios. Os CPFs são
gerados para satisfazer o algoritmo de validação e não estão associados a
nenhum outro dado. As ordens são construídas com as mesmas operações de
domínio usadas pela aplicação, portanto respeitam todas as regras.
"""

from __future__ import annotations

from datetime import datetime

from ...domain import order_operations as ops
from ...domain.clock import BRT, DEFAULT_ACTOR
from ...domain.deadlines import default_due_date
from ...models import (
    Client,
    Equipment,
    ItemKind,
    OrderCreate,
    OrderItemCreate,
    OrderStatus,
    PaymentCreate,
    Rating,
    ServiceOrder,
    Technician,
)

S = OrderStatus


def _at(day: int, hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 10, day, hour, minute, tzinfo=BRT)


def seed_clients() -> list[Client]:
    rows = [
        ("1", "Marina Oliveira", "39053344705", "marina@example.test", "11988881001"),
        ("2", "Rafael Santos", "71460238001", "rafael@example.test", "11977772002"),
        ("3", "Camila Souza", "28641593098", "camila@example.test", "21966663003"),
        ("4", "João Pereira", "85319726473", "joao@example.test", "1133334004"),
        ("5", "Beatriz Lima", "14725836982", "beatriz@example.test", "31955555005"),
        ("6", "Lucas Almeida", "96231857409", "lucas@example.test", "41944446006"),
    ]
    return [Client(id=i, name=n, cpf=c, email=e, phone=p) for i, n, c, e, p in rows]


def seed_technicians() -> list[Technician]:
    return [
        Technician(id="1", name="Carlos Mendes", specialty="Computadores e notebooks"),
        Technician(id="2", name="Fernanda Rocha", specialty="Consoles"),
        Technician(id="3", name="Diego Martins", specialty="Celulares e tablets"),
    ]


def seed_equipment() -> list[Equipment]:
    rows = [
        ("1", "1", "Notebook", "Lenovo", "IdeaPad 3", "PF3XK21A", "Acompanha carregador."),
        ("2", "2", "Console", "Microsoft", "Xbox Series S", "XSS-0042-BR", ""),
        ("3", "3", "Celular", "Samsung", "Galaxy A54", "", "Tela com pequeno risco no canto."),
        ("4", "4", "Computador", "Dell", "OptiPlex 3080", "DL3080-7781", ""),
        ("5", "5", "Tablet", "Apple", "iPad 9", "DMPX9Q2KL", "Sem capa."),
        ("6", "4", "Notebook", "Acer", "Aspire 5", "", ""),
        ("7", "5", "Celular", "Motorola", "Moto G84", "", ""),
        ("8", "1", "Console", "Sony", "PlayStation 5", "PS5-CFI-1214", ""),
    ]
    return [
        Equipment(id=i, client_id=c, kind=k, brand=b, model=m, serial_number=s, notes=n)
        for i, c, k, b, m, s, n in rows
    ]


class _Order:
    """Pequeno roteiro para montar ordens de demonstração com as regras reais."""

    def __init__(self, code: str, client_id: str, equipment_id: str, problem: str, at: datetime) -> None:
        data = OrderCreate(client_id=client_id, equipment_id=equipment_id, problem=problem)
        self.order = ops.open_order(code, data, at, DEFAULT_ACTOR)

    def tech(self, technician: Technician, at: datetime) -> _Order:
        self.order = ops.assign_technician(self.order, technician, None, at, DEFAULT_ACTOR)
        return self

    def status(self, target: OrderStatus, at: datetime, reason: str = "") -> _Order:
        self.order = ops.change_status(self.order, target, at, DEFAULT_ACTOR, reason)
        return self

    def diagnosis(self, text: str, at: datetime) -> _Order:
        self.order = ops.record_diagnosis(self.order, text, at, DEFAULT_ACTOR)
        return self

    def item(self, kind: ItemKind, description: str, price: str, at: datetime, quantity: int = 1) -> _Order:
        data = OrderItemCreate(kind=kind, description=description, quantity=quantity, unit_price=price)
        self.order = ops.add_item(self.order, data, at, DEFAULT_ACTOR)
        return self

    def pay(self, amount: str, method: str, at: datetime) -> _Order:
        self.order = ops.add_payment(self.order, PaymentCreate(amount=amount, method=method), at, DEFAULT_ACTOR)
        return self


def seed_orders() -> list[ServiceOrder]:
    carlos, fernanda, diego = seed_technicians()
    svc, part = ItemKind.SERVICE, ItemKind.PART

    delivered = (
        _Order("OS-2026-00120", "3", "3", "Falha de carregamento", _at(1, 9))
        .tech(diego, _at(1, 9, 30)).status(S.ANALYSIS, _at(1, 10))
        .diagnosis("Conector USB-C oxidado.", _at(1, 14))
        .item(svc, "Troca do conector de carga", "180,00", _at(1, 14, 10))
        .item(part, "Conector USB-C", "45,00", _at(1, 14, 12))
        .status(S.AWAITING_APPROVAL, _at(1, 14, 15)).status(S.REPAIR, _at(2, 9))
        .status(S.DONE, _at(3, 16)).pay("225,00", "PIX", _at(4, 10)).status(S.DELIVERED, _at(4, 10, 5))
    )
    cancelled = (
        _Order("OS-2026-00121", "4", "6", "Não liga", _at(5, 11))
        .tech(carlos, _at(5, 11, 20)).status(S.ANALYSIS, _at(5, 13))
        .diagnosis("Placa-mãe com curto no circuito de alimentação.", _at(6, 10))
        .item(svc, "Substituição da placa-mãe", "350,00", _at(6, 10, 5))
        .item(part, "Placa-mãe Aspire 5", "890,00", _at(6, 10, 6))
        .status(S.AWAITING_APPROVAL, _at(6, 10, 10))
        .status(S.CANCELLED, _at(7, 15), reason="Cliente não aprovou o orçamento.")
    )
    done_partial = (
        _Order("OS-2026-00122", "5", "5", "Imagem piscando na tela", _at(8, 10))
        .tech(diego, _at(8, 10, 30)).status(S.ANALYSIS, _at(8, 11))
        .diagnosis("Cabo flat do display danificado.", _at(8, 16))
        .item(svc, "Desmontagem e reparo do display", "120,00", _at(8, 16, 5))
        .item(part, "Cabo flat do display", "45,50", _at(8, 16, 6), quantity=2)
        .status(S.AWAITING_APPROVAL, _at(8, 16, 10)).status(S.REPAIR, _at(9, 9))
        .status(S.DONE, _at(10, 17)).pay("100,00", "PIX", _at(10, 17, 30))
    )
    awaiting = (
        _Order("OS-2026-00123", "4", "4", "Desliga sozinho após alguns minutos", _at(12, 9))
        .tech(carlos, _at(12, 9, 15)).status(S.ANALYSIS, _at(12, 10))
        .diagnosis("Fonte de alimentação danificada.", _at(13, 11))
        .item(svc, "Substituição da fonte", "90,00", _at(13, 11, 5))
        .item(part, "Fonte ATX 500 W", "320,00", _at(13, 11, 6))
        .status(S.AWAITING_APPROVAL, _at(13, 11, 10))
    )
    analysis = (
        _Order("OS-2026-00124", "2", "2", "Desligamento inesperado durante jogos", _at(14, 14))
        .tech(fernanda, _at(14, 14, 30)).status(S.ANALYSIS, _at(15, 9))
    )
    repair = (
        _Order("OS-2026-00125", "1", "1", "Superaquecimento", _at(15, 10))
        .tech(carlos, _at(15, 10, 20)).status(S.ANALYSIS, _at(15, 11))
        .diagnosis("Pasta térmica ressecada e cooler obstruído.", _at(16, 9))
        .item(svc, "Limpeza interna e troca de pasta térmica", "150,00", _at(16, 9, 5))
        .item(part, "Pasta térmica", "35,00", _at(16, 9, 6))
        .status(S.AWAITING_APPROVAL, _at(16, 9, 10)).status(S.REPAIR, _at(16, 15))
    )
    received = _Order("OS-2026-00126", "5", "7", "Não reconhece o chip", _at(17, 16))

    orders = [received, repair, analysis, awaiting, done_partial, cancelled, delivered]
    # Avaliação da cliente após a entrega (add-service-rating).
    rating = Rating(score=9, comment="Atendimento rápido e explicaram tudo antes de trocar a peça.", at=_at(5, 18))
    delivered.order = delivered.order.model_copy(update={"rating": rating})
    # Previsão padrão de 7 dias (add-deadlines-and-warranty).
    return [o.order.model_copy(update={"due_date": default_due_date(o.order.opened_at)}) for o in orders]
