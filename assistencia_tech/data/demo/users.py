"""Contas de demonstração (somente modo demonstração).

ATENÇÃO: senhas de TESTE, públicas e documentadas em ``docs/DEMO_USERS.md``.
Elas existem apenas nos dados fictícios em memória e não são aceitas por
nenhuma integração real. Os hashes foram precalculados com
``domain.passwords.hash_password`` (PBKDF2-SHA256, 600.000 iterações) para
não atrasar a inicialização da aplicação.
"""

from __future__ import annotations

from dataclasses import dataclass

from ...models import Role, UserAccount

# Senhas de teste por conta (usadas pelo acesso rápido e pelos testes).
DEMO_PASSWORDS: dict[str, str] = {
    "admin@assistencia.test": "admin2026",
    "atendimento@assistencia.test": "atende2026",
    "carlos@assistencia.test": "tecnico2026",
    "fernanda@assistencia.test": "tecnico2026",
    "diego@assistencia.test": "tecnico2026",
    "marina@example.test": "cliente2026",
    "camila@example.test": "cliente2026",
}

_HASHES = {
    "admin": "pbkdf2_sha256$600000$3e492aa05c53ac386f9ef2c449241485$13147159a7989c28227754464d5a659cc9b0304cd73289c71603e35804b3b399",
    "atendente": "pbkdf2_sha256$600000$79b39f923963a92346a9c9d054ef97df$f9d26455552d350d203fa25344f5aeac417a3752caf234b7fcb446d61411e146",
    "carlos": "pbkdf2_sha256$600000$274f827f036f9e5b42e1b78da2ecbdc2$73b3ca39fc5fefd605771311291a479bf73570471bce56826a95b75b8fa795ec",
    "fernanda": "pbkdf2_sha256$600000$0cc3a9821241f3399a0eebf8867d324e$b5af8b3f5cac18bde41a6948d65b51c7ad02232396b506dc626f48a7e75eb922",
    "diego": "pbkdf2_sha256$600000$7ff9b30249dfdf2fd49b467ebff29778$899307b9acd44ac413e43c61fdbedb56eace79b8b0e8f17971641bc5f5d588b9",
    "marina": "pbkdf2_sha256$600000$a8f958fd3a339df85866e31a977e49f7$04777d097c1155c9bdb02bfb3c932db48fa1cff9ef287395cf59eb0a44cad9ba",
    "camila": "pbkdf2_sha256$600000$ab1512154aef56ea265e033f508779fa$ac4af107503748733b4114ebedf90605e019f4be45ef8e34443577a254bfbe95",
}


@dataclass(frozen=True)
class DemoAccount:
    key: str
    label: str
    description: str
    email: str


# Acesso rápido exibido na tela de login (uma conta por perfil).
DEMO_ACCOUNTS: tuple[DemoAccount, ...] = (
    DemoAccount("admin", "Administrador", "Acesso completo", "admin@assistencia.test"),
    DemoAccount("atendente", "Atendente", "Balcão e pagamentos", "atendimento@assistencia.test"),
    DemoAccount("tecnico", "Técnico", "Carlos Mendes", "carlos@assistencia.test"),
    DemoAccount("cliente", "Cliente", "Marina Oliveira", "marina@example.test"),
)


def seed_users() -> list[UserAccount]:
    rows = [
        ("1", "Ana Ribeiro", "admin@assistencia.test", Role.ADMIN, "admin", None, None),
        ("2", "Paulo Nunes", "atendimento@assistencia.test", Role.ATTENDANT, "atendente", None, None),
        ("3", "Carlos Mendes", "carlos@assistencia.test", Role.TECHNICIAN, "carlos", None, "1"),
        ("4", "Fernanda Rocha", "fernanda@assistencia.test", Role.TECHNICIAN, "fernanda", None, "2"),
        ("5", "Diego Martins", "diego@assistencia.test", Role.TECHNICIAN, "diego", None, "3"),
        ("6", "Marina Oliveira", "marina@example.test", Role.CLIENT, "marina", "1", None),
        ("7", "Camila Souza", "camila@example.test", Role.CLIENT, "camila", "3", None),
    ]
    return [
        UserAccount(id=i, name=n, email=e, role=r, password_hash=_HASHES[h], client_id=c, technician_id=t)
        for i, n, e, r, h, c, t in rows
    ]
