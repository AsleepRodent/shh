from typing import Any
from textual.screen import Screen as Textual_Screen

class Screen(Textual_Screen):
    def __init__(self, parent: Any) -> None:
        self.parent: Any = parent
        super().__init__()