"""Configuração do Reflex.

Publicado (add-public-deployment), o frontend precisa do endereço público do
backend: vem de ``ASSISTENCIA_PUBLIC_URL`` ou, no Render, de
``RENDER_EXTERNAL_URL``. Sem nenhuma das duas (desenvolvimento), valem os
padrões do Reflex. ``REFLEX_API_URL`` continua tendo prioridade.
"""

import os

import reflex as rx

PUBLIC_URL = (os.environ.get("ASSISTENCIA_PUBLIC_URL") or os.environ.get("RENDER_EXTERNAL_URL") or "").rstrip("/")

config = rx.Config(
    app_name="assistencia_tech",
    telemetry_enabled=False,
    **({"api_url": PUBLIC_URL, "deploy_url": PUBLIC_URL} if PUBLIC_URL else {}),
)
