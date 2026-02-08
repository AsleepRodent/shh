from typing import Any

from ..module import Module

class Interface(Module):
    def __init__(self, parent: Any) -> None:
        super().__init__("Interface", parent)