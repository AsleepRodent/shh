from textual import on
from textual.events import Key
from ..screen import Screen
from textual.widgets import Label, Button, ContentSwitcher, Input
from textual.containers import Vertical, Center, Middle, Horizontal

class Introduction(Screen):
    def __init__(self, interface, **kwargs):
        super().__init__(interface, **kwargs)
        self.step = 1
        self.max_steps = 3
        self.validation_timer = None
        self.current_suggestion = ""

    def compose(self):
        with Center():
            with Middle():
                with Vertical(id="panel"):
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

    def on_input_changed(self, event: Input.Changed):
        if event.input.id == "username":
            if self.validation_timer:
                self.validation_timer.stop()
            
            self.query_one("#status_msg", Label).update("")
            self.current_suggestion = ""
            self.validation_timer = self.set_timer(0.5, self.validate_username)

    def validate_username(self):
        input_widget = self.query_one("#username", Input)
        msg = self.query_one("#status_msg", Label)
        username = input_widget.value.strip()
        profile = self.interface.client.get_module("profile")

        if not username:
            msg.update("")
            return

        if profile.exists(username):
            self.current_suggestion = profile.suggest_username(username)
            msg.update(f"Username taken. Try: [b]{self.current_suggestion}[/] [dim](TAB to use)[/]")
            msg.set_class(True, "error_msg")
            msg.set_class(False, "success_msg")
        else:
            self.current_suggestion = ""
            msg.update("Username available!")
            msg.set_class(True, "success_msg")
            msg.set_class(False, "error_msg")

    def on_key(self, event: Key):
        if self.step == 2:
            username_input = self.query_one("#username", Input)
            
            if username_input.has_focus and event.key == "tab" and self.current_suggestion:
                event.stop()
                event.prevent_default()
                username_input.value = self.current_suggestion
                if self.validation_timer:
                    self.validation_timer.stop()
                self.validate_username()
                self.query_one("#alias", Input).focus()

    @on(Input.Submitted)
    def handle_submit(self):
        self.on_button_pressed(Button(id="next_btn"))

    def on_button_pressed(self, event):
        if event.button.id == "next_btn":
            if self.step == 2:
                username = self.query_one("#username", Input).value.strip()
                profile = self.interface.client.get_module("profile")
                if not username or profile.exists(username):
                    self.app.notify("Username not available", severity="error")
                    return 
                
            if self.step < self.max_steps:
                self.step += 1
            else:
                self.finish_setup()
        elif event.button.id == "back_btn":
            if self.step > 1: self.step -= 1

        self.query_one(ContentSwitcher).current = f"step_{self.step}"
        self.update_buttons()

    def update_buttons(self):
        btn_next = self.query_one("#next_btn", Button)
        btn_next.label = "Finish" if self.step == self.max_steps else "Next"
        self.query_one("#back_btn", Button).disabled = (self.step == 1)

    def finish_setup(self):
        profile = self.interface.client.get_module("profile")
        if profile:
            u = self.query_one("#username", Input).value
            a = self.query_one("#alias", Input).value
            
            success = profile.create_profile(username=u, alias=a)
            
            if success:
                self.interface.switch_screen("selector")
            else:
                self.app.notify("Failed to create profile", severity="error")