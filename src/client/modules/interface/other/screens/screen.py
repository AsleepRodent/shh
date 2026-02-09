from typing import Any

from textual.screen import Screen as Textual_Screen


class Screen(Textual_Screen):
    def __init__(self, interface_instance: Any, **initialization_kwargs: Any) -> None:
        self.interface: Any = interface_instance
        super().__init__(**initialization_kwargs)