from textual.app import App

from .modules.module import Module

from .modules.interface.interface import Interface
from .modules.network.network import Network
from .modules.profile.profile import Profile
from .modules.graph.graph import Graph

class Client(App):
    def __init__(self, url: str, port: int) -> None:
        self.url: str = url
        self.port: int = port

        self.modules: dict[str, Module] = {
            "interface": Interface(self),
            "network": Network(self),
            "profile": Profile(self),
            "graph": Graph(self)
        }

        super().__init__()

    def getModule(self, name: str) -> Module | None:
        for module in self.modules.values():
            if module.name.lower() == name.lower():
                return module
        return None

    def start(self) -> None:
        self.run()
