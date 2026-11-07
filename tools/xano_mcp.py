"""Cliente mínimo do Xano Developer MCP pela linha de comando.

Permite consultar a documentação oficial e validar XanoScript sem depender de
um agente com MCP configurado:

    python -m tools.xano_mcp list
    python -m tools.xano_mcp call xano_xanoscript_docs '{}'
    python -m tools.xano_mcp call xano_xanoscript_docs '{"topic": "table"}'
    python -m tools.xano_mcp validate xano/tables/cliente.xs [outros.xs ...]
"""

from __future__ import annotations

import json
import queue
import subprocess
import sys
import threading
from typing import Any

COMMAND = ["cmd", "/c", "npx", "-y", "@xano/developer-mcp@2.2.6"]


class McpClient:
    def __init__(self) -> None:
        self.proc = subprocess.Popen(
            COMMAND, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, encoding="utf-8", bufsize=1,
        )
        self._lines: queue.Queue[str] = queue.Queue()
        threading.Thread(target=self._read, daemon=True).start()
        self._id = 0
        self._request("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                                     "clientInfo": {"name": "assistencia-tech", "version": "1"}}, timeout=240)
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def _read(self) -> None:
        for line in self.proc.stdout:  # type: ignore[union-attr]
            self._lines.put(line)

    def _send(self, message: dict[str, Any]) -> None:
        self.proc.stdin.write(json.dumps(message) + "\n")  # type: ignore[union-attr]
        self.proc.stdin.flush()  # type: ignore[union-attr]

    def _request(self, method: str, params: dict[str, Any], timeout: float = 120) -> dict[str, Any]:
        self._id += 1
        self._send({"jsonrpc": "2.0", "id": self._id, "method": method, "params": params})
        while True:
            data = json.loads(self._lines.get(timeout=timeout))
            if data.get("id") == self._id:
                if "error" in data:
                    raise RuntimeError(data["error"])
                return data["result"]

    def tools(self) -> list[dict[str, Any]]:
        return self._request("tools/list", {})["tools"]

    def call(self, name: str, arguments: dict[str, Any]) -> str:
        result = self._request("tools/call", {"name": name, "arguments": arguments})
        return "\n".join(c.get("text", "") for c in result.get("content", []) if c.get("type") == "text")

    def close(self) -> None:
        self.proc.kill()


def main(argv: list[str]) -> int:
    client = McpClient()
    try:
        if argv[0] == "list":
            for tool in client.tools():
                print(f"## {tool['name']}\n{tool.get('description', '')}\n"
                      f"schema: {json.dumps(tool.get('inputSchema', {}), ensure_ascii=False)}\n")
        elif argv[0] == "call":
            print(client.call(argv[1], json.loads(argv[2]) if len(argv) > 2 else {}))
        elif argv[0] == "validate":
            failed = 0
            for path in argv[1:]:
                code = open(path, encoding="utf-8").read()
                text = client.call("xano_validate_xanoscript", {"code": code})
                ok = "valid" in text.lower() and "error" not in text.lower()
                failed += not ok
                print(f"=== {path}: {'OK' if ok else 'ERROS'}\n{text}\n")
            return 1 if failed else 0
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
