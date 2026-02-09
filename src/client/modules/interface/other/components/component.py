from typing import Any

from textual.widgets import Static


class Component(Static):
    def __init__(self, **initialization_kwargs: Any) -> None:
        super().__init__(**initialization_kwargs)