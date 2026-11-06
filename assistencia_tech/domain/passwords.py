"""Hash e verificação de senhas (PBKDF2-SHA256) e política de senha.

Formato armazenado: ``pbkdf2_sha256$<iterações>$<sal hex>$<hash hex>``. O número
de iterações faz parte do valor, o que permite aumentá-lo no futuro sem
invalidar senhas existentes. Senhas nunca são registradas em logs.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets

from ..data.errors import ValidationError

ALGORITHM = "pbkdf2_sha256"
DEFAULT_ITERATIONS = 600_000  # recomendação OWASP para PBKDF2-SHA256
SALT_BYTES = 16
MIN_LENGTH = 8
POLICY_MESSAGE = "A senha deve ter no mínimo 8 caracteres, com ao menos uma letra e um número."


def _derive(password: str, salt: bytes, iterations: int) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)


def hash_password(password: str, *, iterations: int = DEFAULT_ITERATIONS, salt: bytes | None = None) -> str:
    salt = salt if salt is not None else secrets.token_bytes(SALT_BYTES)
    digest = _derive(password, salt, iterations)
    return f"{ALGORITHM}${iterations}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Compara em tempo constante; valores malformados nunca validam."""
    try:
        algorithm, iterations, salt_hex, digest_hex = stored.split("$")
        if algorithm != ALGORITHM:
            return False
        expected = bytes.fromhex(digest_hex)
        actual = _derive(password, bytes.fromhex(salt_hex), int(iterations))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual, expected)


def check_password_policy(password: str) -> None:
    if (
        len(password) < MIN_LENGTH
        or not any(ch.isalpha() for ch in password)
        or not any(ch.isdigit() for ch in password)
    ):
        raise ValidationError(POLICY_MESSAGE)
