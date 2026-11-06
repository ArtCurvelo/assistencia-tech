import pytest


@pytest.fixture
def anyio_backend():
    # Testes assíncronos rodam apenas com asyncio (plugin do anyio).
    return "asyncio"
