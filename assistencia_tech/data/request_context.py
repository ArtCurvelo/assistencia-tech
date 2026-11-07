"""Token do backend vinculado à requisição em andamento (decisão D12).

Com a fonte Xano, o login devolve um JWT que fica guardado na sessão do
servidor, nunca no navegador. Antes de usar os repositórios, o serviço de
autenticação coloca o JWT da sessão neste contexto; o cliente HTTP o lê para
enviar ``Authorization: Bearer``. ``ContextVar`` isola cada evento do Reflex
(cada tarefa assíncrona tem sua própria cópia do contexto).

O provedor de autenticação também usa este módulo para entregar ao serviço o
token recém-emitido no login ou no cadastro (``issued``).
"""

from __future__ import annotations

from contextvars import ContextVar

_current: ContextVar[str | None] = ContextVar("backend_token", default=None)
_issued: ContextVar[str | None] = ContextVar("backend_token_issued", default=None)


def use_backend_token(token: str | None) -> None:
    """Define o token usado nas próximas chamadas desta requisição."""
    _current.set(token)


def current_backend_token() -> str | None:
    return _current.get()


def issue_backend_token(token: str) -> None:
    """Chamado pelo provedor ao receber um token novo (login ou cadastro)."""
    _issued.set(token)
    _current.set(token)


def take_issued_token() -> str | None:
    """Retorna e limpa o token emitido nesta requisição (``None`` no modo demonstração)."""
    token = _issued.get()
    _issued.set(None)
    return token
