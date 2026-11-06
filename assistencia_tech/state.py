import reflex as rx
from .services.demo_data import initial_clients, initial_equipment, initial_orders

class AppState(rx.State):
    tracking_code: str = ""
    tracking_message: str = ""
    auth_message: str = ""
    client_search: str = ""
    order_search: str = ""
    clients: list[dict[str, str]] = initial_clients()
    equipment: list[dict[str, str]] = initial_equipment()
    orders: list[dict[str, str]] = initial_orders()
    next_client_id: int = 4
    next_equipment_id: int = 4
    next_order_id: int = 126

    @rx.var
    def client_names(self) -> list[str]:
        return [client["name"] for client in self.clients]

    @rx.var
    def open_orders(self) -> int:
        return sum(1 for order in self.orders if order["status"] != "Concluído")

    @rx.var
    def filtered_clients(self) -> list[dict[str, str]]:
        query = self.client_search.lower().strip()
        if not query:
            return self.clients
        return [c for c in self.clients if query in c["name"].lower() or query in c["email"].lower()]

    @rx.var
    def filtered_orders(self) -> list[dict[str, str]]:
        query = self.order_search.lower().strip()
        if not query:
            return self.orders
        return [o for o in self.orders if query in o["code"].lower() or query in o["client"].lower() or query in o["device"].lower()]

    def set_tracking_code(self, value: str):
        self.tracking_code = value
        self.tracking_message = ""

    def lookup_order(self):
        code = self.tracking_code.strip().upper()
        match = next((o for o in self.orders if o["code"].upper() == code), None)
        if match:
            self.tracking_message = f'{match["code"]}: {match["status"]} — {match["device"]}. Consulta demonstrativa.'
        else:
            self.tracking_message = "Código não encontrado na base demonstrativa."

    def demo_login(self, form_data: dict):
        self.auth_message = "Login demonstrativo: autenticação real ainda não está conectada."

    def demo_register(self, form_data: dict):
        self.auth_message = "Cadastro demonstrativo: os dados não foram salvos nem enviados."

    def set_client_search(self, value: str):
        self.client_search = value

    def set_order_search(self, value: str):
        self.order_search = value

    def add_client(self, form_data: dict):
        name = form_data.get("name", "").strip()
        email = form_data.get("email", "").strip()
        phone = form_data.get("phone", "").strip() or "Não informado"
        if not name or not email:
            return
        self.clients = self.clients + [{"id": str(self.next_client_id), "name": name, "email": email, "phone": phone}]
        self.next_client_id += 1

    def add_equipment(self, form_data: dict):
        client = form_data.get("client", "").strip()
        kind = form_data.get("kind", "").strip()
        model = form_data.get("model", "").strip()
        if not client or not kind or not model:
            return
        self.equipment = self.equipment + [{"id": str(self.next_equipment_id), "client": client, "kind": kind, "model": model}]
        self.next_equipment_id += 1

    def add_order(self, form_data: dict):
        client = form_data.get("client", "").strip()
        device = form_data.get("device", "").strip()
        problem = form_data.get("problem", "").strip()
        if not client or not device or not problem:
            return
        code = f"OS-2026-{self.next_order_id}"
        self.orders = [{"code": code, "client": client, "device": device, "problem": problem, "status": "Recebido"}] + self.orders
        self.next_order_id += 1

    def update_order_status(self, code: str, status: str):
        allowed = {"Recebido", "Em análise", "Em reparo", "Concluído"}
        if status not in allowed:
            return
        self.orders = [
            {**order, "status": status} if order["code"] == code else order
            for order in self.orders
        ]
