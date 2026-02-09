from ..screen import Screen

class RoomSelector(Screen):
    def __init__(self, interface_instance, **initialization_kwargs) -> None:
        super().__init__(interface_instance, **initialization_kwargs)
        self.rooms = []
        self.selected_room = None