"""Regras do projeto verificadas automaticamente (mudança add-continuous-integration)."""

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MAX_LINES = 1000
JWT_RE = re.compile(rb"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}")


def tracked_files() -> list[Path]:
    """Arquivos versionados (os mesmos no computador e no GitHub)."""
    try:
        out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("git indisponível")
    return [ROOT / name for name in out.decode().split("\0") if name]


def too_long(paths: list[Path]) -> list[str]:
    problems = []
    for path in paths:
        if path.suffix == ".py" and path.exists():
            lines = len(path.read_text(encoding="utf-8").splitlines())
            if lines >= MAX_LINES:
                problems.append(f"{path.relative_to(ROOT)}: {lines} linhas")
    return problems


def with_tokens(paths: list[Path]) -> list[str]:
    return [str(p.relative_to(ROOT)) for p in paths if p.is_file() and JWT_RE.search(p.read_bytes())]


def test_python_files_stay_under_the_line_limit():
    assert too_long(tracked_files()) == []


def test_no_env_file_is_versioned():
    env_files = [p.name for p in tracked_files()
                 if p.name == ".env" or (p.name.startswith(".env.") and p.name != ".env.example")]
    assert env_files == []


def test_no_jwt_is_versioned():
    assert with_tokens(tracked_files()) == []


def test_rules_catch_offending_files(tmp_path, monkeypatch):
    monkeypatch.setitem(globals(), "ROOT", tmp_path)
    big = tmp_path / "grande.py"
    big.write_text("x = 1\n" * MAX_LINES, encoding="utf-8")
    leaked = tmp_path / "vazou.txt"
    # Montado por partes para que este arquivo não contenha um token literal.
    leaked.write_bytes(b'token = "' + b"eyJhbGciOiJIUzI1NiJ9" + b"." + b"eyJzdWIiOiIxMjM0NTY3ODkwIn0" + b'.x"')
    assert too_long([big]) == [f"grande.py: {MAX_LINES} linhas"]
    assert with_tokens([leaked, big]) == ["vazou.txt"]
