import pytest

from assistencia_tech.state.base import safe_next


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("/admin/ordens", "/admin/ordens"),
        ("/admin/ordens/OS-2026-00125", "/admin/ordens/OS-2026-00125"),
        ("//exemplo.invalid/roubo", "/admin"),
        ("https://exemplo.invalid", "/admin"),
        ("/\\exemplo.invalid", "/admin"),
        ("", "/admin"),
        (None, "/admin"),
    ],
)
def test_safe_next_only_accepts_internal_paths(value, expected):
    assert safe_next(value, "/admin") == expected
