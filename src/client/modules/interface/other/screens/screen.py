from textual.screen import Screen as Textual_Screen

class Screen(Textual_Screen):
    def __init__(self, interface, **kwargs):
        self.interface = interface
        super().__init__(**kwargs)