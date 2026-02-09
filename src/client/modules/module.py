from typing import Any


class Module:
    def __init__(self, module_name: str, client_instance: Any) -> None:
        self.client: Any = client_instance
        self.name: str = module_name