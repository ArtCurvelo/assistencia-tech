"""Erros padronizados da camada de acesso a dados.

Cada erro carrega uma ``user_message`` em português, segura para exibição na
interface. Detalhes técnicos (URLs, status HTTP, corpos de resposta) ficam em
``detail`` e devem ser enviados apenas ao log.
"""

from __future__ import annotations


class DataAccessError(Exception):
    """Base de todos os erros de acesso a dados."""

    default_message = "Não foi possível concluir a operação. Tente novamente."

    def __init__(self, user_message: str | None = None, *, detail: str | None = None) -> None:
        self.user_message = user_message or self.default_message
        self.detail = detail
        super().__init__(self.user_message)


class ConfigurationError(DataAccessError):
    default_message = "A fonte de dados não está configurada corretamente."


class ValidationError(DataAccessError):
    default_message = "Os dados informados são inválidos."


class UnauthorizedError(DataAccessError):
    default_message = "Acesso não autorizado. Verifique suas permissões."


class AuthenticationError(DataAccessError):
    """Sem sessão válida, sessão expirada ou credenciais recusadas."""

    default_message = "Sua sessão não é válida. Entre novamente para continuar."


class PermissionDeniedError(DataAccessError):
    """Usuário autenticado sem permissão para a ação."""

    default_message = "Seu perfil não tem permissão para esta ação."


class NotFoundError(DataAccessError):
    default_message = "O registro solicitado não foi encontrado."


class ServiceUnavailableError(DataAccessError):
    default_message = "O serviço está indisponível no momento. Tente novamente em instantes."


class ContractPendingError(DataAccessError):
    default_message = "Esta funcionalidade ainda não está integrada ao backend."


class UnexpectedError(DataAccessError):
    default_message = "Ocorreu um erro inesperado. Tente novamente."
