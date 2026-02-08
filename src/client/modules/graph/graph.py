from typing import Any

from ..module import Module

class Graph(Module):
    def __init__(self, parent: Any) -> None:
        super().__init__("Graph", parent)