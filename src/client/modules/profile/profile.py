from typing import Any

from ..module import Module

class Profile(Module):
    def __init__(self, parent: Any) -> None:
        super().__init__("Profile", parent)