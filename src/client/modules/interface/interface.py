from ..module import Module

from .other.screens.introduction.introduction import Introduction    
from .other.screens.profile_selector.profile_selector import ProfileSelector

class Interface(Module):
    def __init__(self, client):
        super().__init__("Interface", client)
        
        self.screens = {
            "introduction": Introduction(self, id="introduction"),
            "profile_selector": ProfileSelector(self, id="profile_selector")
        }
        self.current_screen = self.screens["introduction"]

    def switch_screen(self, screen_name):
        if screen_name in self.screens:
            self.current_screen = self.screens[screen_name]
            self.client.push_screen(self.current_screen)