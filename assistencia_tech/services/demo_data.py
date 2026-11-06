"""Dados fictícios para a demonstração. Substituir por repositórios/API após conhecer os contratos reais."""

def initial_clients():
    return [
        {"id": "1", "name": "Marina Oliveira", "email": "marina@example.test", "phone": "(11) 98888-1001"},
        {"id": "2", "name": "Rafael Santos", "email": "rafael@example.test", "phone": "(11) 97777-2002"},
        {"id": "3", "name": "Camila Souza", "email": "camila@example.test", "phone": "(11) 96666-3003"},
    ]

def initial_equipment():
    return [
        {"id": "1", "client": "Marina Oliveira", "kind": "Notebook", "model": "Lenovo IdeaPad"},
        {"id": "2", "client": "Rafael Santos", "kind": "Console", "model": "Xbox Series S"},
        {"id": "3", "client": "Camila Souza", "kind": "Celular", "model": "Samsung Galaxy"},
    ]

def initial_orders():
    return [
        {"code": "OS-2026-00125", "client": "Marina Oliveira", "device": "Lenovo IdeaPad", "problem": "Superaquecimento", "status": "Em reparo"},
        {"code": "OS-2026-00124", "client": "Rafael Santos", "device": "Xbox Series S", "problem": "Desligamento inesperado", "status": "Em análise"},
        {"code": "OS-2026-00123", "client": "Camila Souza", "device": "Samsung Galaxy", "problem": "Falha de carregamento", "status": "Concluído"},
    ]
