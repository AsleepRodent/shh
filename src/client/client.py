from textual.app import App
from pathlib import Path

from .modules.interface.interface import Interface
from .modules.network.network import Network
from .modules.profile.profile import Profile
from .modules.graph.graph import Graph

class Client(App):
    CSS_PATH = "style.tcss"

    def __init__(self, directory):
        self.directory = Path(directory)
        super().__init__()
        
        self.modules = {}
        self.modules["profile"] = Profile(self, self.directory)
        self.modules["network"] = Network(self)
        self.modules["graph"] = Graph(self)
        self.modules["interface"] = Interface(self)

    def on_mount(self):
        profile = self.get_module("profile")
        interface = self.get_module("interface")
        
        if interface and profile:
            first_run = profile.data.get("global", {}).get("first_run", True)
            
            if first_run:
                interface.switch_screen("introduction")
            else:
                interface.switch_screen("profile_selector")

    def get_module(self, name):
        return self.modules.get(name.lower())

    def start(self):
        self.run()