from typing import Any, Optional

from textual import on
from textual.containers import Center, Horizontal, Middle, Vertical
from textual.events import Key
from textual.widgets import Button, ContentSwitcher, Input, Label

from ..screen import Screen


class Introduction(Screen):
    def __init__(self, interface_instance: Any, **initialization_kwargs: Any) -> None:
        super().__init__(interface_instance, **initialization_kwargs)
        self.current_suggestion: str = ""
        self.max_steps: int = 3
        self.step: int = 1
        self.validation_timer: Optional[Any] = None

    def compose(self):
        with Center():
            with Middle():
                with Vertical(id="modal-panel"):
                    with ContentSwitcher(initial="step_1"):
                        with Vertical(id="step_1"):
                            yield Label("WELCOME TO SHH", classes="title")
                            yield Label("A secure platform for developers.", classes="desc")
                        
                        with Vertical(id="step_2"):
                            yield Label("CREATE PROFILE", classes="title")
                            yield Input(placeholder="Username (Required)", id="username")
                            yield Label("", id="status_msg")
                            yield Input(placeholder="Alias (Optional)", id="alias")
                        
                        with Vertical(id="step_3"):
                            yield Label("ALL SET", classes="title")
                            yield Label("Introduction completed successfully.", classes="desc")
                            yield Label("Press 'Finish' to start exploring.", classes="desc")

                    with Center():
                        with Horizontal(id="btn_group"):
                            yield Button("Back", id="back_btn")
                            yield Button("Next", id="next_btn")

    def finish_setup(self) -> None:
        profile_module: Optional[Any] = self.interface.client.get_module("profile")
        if profile_module:
            username_input_value: str = self.query_one("#username", Input).value
            alias_input_value: str = self.query_one("#alias", Input).value
            
            profile_creation_success: bool = profile_module.create_profile(username=username_input_value, alias=alias_input_value)
            
            if profile_creation_success:
                self.interface.switch_screen("profile_selector")
            else:
                self.app.notify("Failed to create profile", severity="error")

    @on(Input.Submitted)
    def handle_submit(self) -> None:
        event = Button.Pressed(self.query_one("#next_btn", Button))
        self.on_button_pressed(event)

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "next_btn":
            if self.step == 2:
                username_value: str = self.query_one("#username", Input).value.strip()
                profile_module: Optional[Any] = self.interface.client.get_module("profile")
                if not profile_module or not username_value or profile_module.exists(username_value):
                    self.app.notify("Username not available", severity="error")
                    return 
                
            if self.step < self.max_steps:
                self.step += 1
            else:
                self.finish_setup()
        elif event.button.id == "back_btn":
            if self.step > 1:
                self.step -= 1

        self.query_one(ContentSwitcher).current = f"step_{self.step}"
        self.update_buttons()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "username":
            if self.validation_timer:
                self.validation_timer.stop()
            
            self.query_one("#status_msg", Label).update("")
            self.current_suggestion = ""
            self.validation_timer = self.set_timer(0.5, self.validate_username)

    def on_key(self, event: Key) -> None:
        if self.step == 2:
            username_input: Input = self.query_one("#username", Input)
            
            if username_input.has_focus and event.key == "tab" and self.current_suggestion:
                event.stop()
                event.prevent_default()
                username_input.value = self.current_suggestion
                if self.validation_timer:
                    self.validation_timer.stop()
                self.validate_username()
                self.query_one("#alias", Input).focus()

    def update_buttons(self) -> None:
        button_next: Button = self.query_one("#next_btn", Button)
        button_next.label = "Finish" if self.step == self.max_steps else "Next"
        self.query_one("#back_btn", Button).disabled = (self.step == 1)

    def validate_username(self) -> None:
        username_input_widget: Input = self.query_one("#username", Input)
        status_message_label: Label = self.query_one("#status_msg", Label)
        username_value: str = username_input_widget.value.strip()
        profile_module: Optional[Any] = self.interface.client.get_module("profile")

        if not username_value:
            status_message_label.update("")
            return
        
        if not profile_module:
            status_message_label.update("Profile module not available")
            return

        if profile_module.exists(username_value):
            self.current_suggestion = profile_module.suggest_username(username_value)
            status_message_label.update(f"Username taken. Try: [b]{self.current_suggestion}[/] [dim](TAB to use)[/]")
            status_message_label.set_class(True, "error_msg")
            status_message_label.set_class(False, "success_msg")
        else:
            self.current_suggestion = ""
            status_message_label.update("Username available!")
            status_message_label.set_class(True, "success_msg")
            status_message_label.set_class(False, "error_msg")