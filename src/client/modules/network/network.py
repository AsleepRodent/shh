from typing import Any

from ..module import Module

class Network(Module):
    def __init__(self, parent: Any) -> None:
        super().__init__("Network", parent)