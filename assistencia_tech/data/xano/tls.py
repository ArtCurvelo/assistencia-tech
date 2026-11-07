"""Contexto TLS que usa o repositório de certificados do sistema operacional.

Nesta máquina de desenvolvimento, o Python (certifi) não reconhece a cadeia de
certificados apresentada ao acessar o Xano, enquanto o Windows a reconhece
(provável inspeção TLS de antivírus ou rede). O ``truststore`` faz o Python
usar o repositório do sistema, mantendo a verificação de certificado ativa.
A verificação nunca é desligada.
"""

from __future__ import annotations

import ssl


def system_ssl_context() -> ssl.SSLContext | bool:
    """Contexto do sistema; sem ``truststore``, volta ao padrão verificado (``True``)."""
    try:
        import truststore
    except ImportError:  # pragma: no cover - dependência declarada em requirements.txt
        return True
    return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
