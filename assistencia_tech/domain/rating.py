"""Avaliação do atendimento e NPS (mudança add-service-rating).

Funções puras. Escala de 0 a 10: promotores 9–10, neutros 7–8, detratores
0–6; NPS = % de promotores − % de detratores, arredondado.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from ..data.errors import ValidationError
from ..models.entities import OrderStatus, Rating, ServiceOrder

QUESTION = "De 0 a 10, quanto você recomendaria a Assistência TECH a um amigo ou familiar?"
MAX_COMMENT = 500
PROMOTER = "Promotor"
NEUTRAL = "Neutro"
DETRACTOR = "Detrator"


def parse_score(value: object) -> int:
    text = str(value if value is not None else "").strip()
    if not text.isdigit() or not 0 <= int(text) <= 10:
        raise ValidationError("A nota deve ser um número inteiro de 0 a 10.")
    return int(text)


def clean_comment(value: object) -> str:
    comment = " ".join(str(value or "").split())
    if len(comment) > MAX_COMMENT:
        raise ValidationError(f"O comentário deve ter no máximo {MAX_COMMENT} caracteres.")
    return comment


def classify(score: int) -> str:
    if score >= 9:
        return PROMOTER
    return NEUTRAL if score >= 7 else DETRACTOR


def ensure_ratable(order: ServiceOrder) -> None:
    if order.status != OrderStatus.DELIVERED:
        raise ValidationError("Só ordens entregues podem ser avaliadas.")
    if order.rating is not None:
        raise ValidationError("Esta ordem já foi avaliada.")


def rate(order: ServiceOrder, score: object, comment: object, at: datetime) -> ServiceOrder:
    """Valida e devolve a ordem com a avaliação (uma única vez, somente após a entrega)."""
    ensure_ratable(order)
    rating = Rating(score=parse_score(score), comment=clean_comment(comment), at=at)
    return order.model_copy(update={"rating": rating})


@dataclass(frozen=True)
class NpsSummary:
    count: int
    promoters: int
    neutrals: int
    detractors: int
    nps: int | None
    average: float | None


def nps_summary(scores: Iterable[int]) -> NpsSummary:
    values = list(scores)
    if not values:
        return NpsSummary(0, 0, 0, 0, None, None)
    groups = [classify(score) for score in values]
    promoters, detractors = groups.count(PROMOTER), groups.count(DETRACTOR)
    count = len(values)
    # Arredondamento comercial (0,5 para cima), não o bancário do ``round``.
    raw = (promoters - detractors) * 100 / count
    nps = int(raw + 0.5) if raw >= 0 else -int(-raw + 0.5)
    return NpsSummary(count, promoters, groups.count(NEUTRAL), detractors, nps, round(sum(values) / count, 1))
