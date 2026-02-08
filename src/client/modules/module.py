from typing import Any

class Module: 
    def __init__(self, name: str, parent: Any) -> None:
        self.name: str = name
        self.parent: Any = parent