from textual import on
from textual.events import Key
from textual.widgets import Label, ListItem, ListView, Button, ContentSwitcher, Input
from textual.containers import Vertical, Center, Middle, Horizontal
from ..screen import Screen

class Selector(Screen):
    def __init__(self, interface, **kwargs):
        super().__init__(interface, **kwargs)
        self.validation_timer = None
        self.current_suggestion = ""

    def compose(self):
        profile_mod = self.interface.client.get_module("profile")
        profiles = profile_mod.data.get("profiles", []) if profile_mod else []
        
        sorted_profiles = sorted(profiles, key=lambda p: p.get("isLastUsed", False), reverse=True)
        
        with Center():
            with Middle():
                with Vertical(id="panel"):
                    with ContentSwitcher(initial="selector_list"):
                        with Vertical(id="selector_list"):
                            yield Label("SELECT PROFILE", classes="title")
                            with ListView(id="profile_list"):
                                for profile in sorted_profiles:
                                    username = profile["username"]
                                    alias = profile.get("social", {}).get("alias", username)
                                    date = profile.get("metadata", {}).get("created_at", "N/A")[:10]
                                    is_last = profile.get("isLastUsed", False)
                                    
                                    with ListItem(id=f"user_{username}"):
                                        with Vertical(classes="card_container"):
                                            with Horizontal():
                                                yield Label(alias, classes="card_alias")
                                                if is_last:
                                                    yield Label("LAST USED", classes="last_badge")
                                            
                                            yield Label(f"@{username}", classes="card_username")
                                            yield Label(f"Created: {date}", classes="card_date")
                                
                                with ListItem(id="create_new_trigger"):
                                    with Center(classes="card_container"):
                                        yield Label("[b]+ Create new profile[/]", classes="desc")

                        with Vertical(id="selector_create"):
                            yield Label("CREATE PROFILE", classes="title")
                            yield Input(placeholder="Username (Required)", id="username")
                            yield Label("", id="status_msg")
                            yield Input(placeholder="Alias (Optional)", id="alias")

                    with Center(id="btn_container"):
                        with Horizontal(id="btn_group"):
                            yield Button("Back", id="back_btn")
                            yield Button("Finish", id="next_btn", variant="primary")

    def on_mount(self):
        self.query_one("#btn_group").display = False

    def on_list_view_selected(self, event: ListView.Selected):
        if event.item.id == "create_new_trigger":
            self.query_one(ContentSwitcher).current = "selector_create"
            self.query_one("#btn_group").display = True
            self.query_one("#username").focus()
        elif event.item.id:
            username = event.item.id.replace("user_", "")
            profile_mod = self.interface.client.get_module("profile")
            if profile_mod.switch_profile(username):
                self.app.notify(f"Profile @{username} active")

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "back_btn":
            self.query_one(ContentSwitcher).current = "selector_list"
            self.query_one("#btn_group").display = False
        elif event.button.id == "next_btn":
            self.finish_setup()

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
        profile_mod = self.interface.client.get_module("profile")

        if not username:
            msg.update("")
            return

        if profile_mod.exists(username):
            self.current_suggestion = profile_mod.suggest_username(username)
            msg.update(f"Username taken. Try: [b]{self.current_suggestion}[/] [dim](TAB to use)[/]")
            msg.set_class(True, "error_msg")
            msg.set_class(False, "success_msg")
        else:
            self.current_suggestion = ""
            msg.update("Username available!")
            msg.set_class(True, "success_msg")
            msg.set_class(False, "error_msg")

    def action_tab_complete(self):
        username_input = self.query_one("#username", Input)
        if username_input.has_focus and self.current_suggestion:
            username_input.value = self.current_suggestion
            if self.validation_timer:
                self.validation_timer.stop()
            self.validate_username()
            self.query_one("#alias", Input).focus()

    def on_key(self, event: Key):
        if event.key == "tab" and self.current_suggestion and self.query_one("#username").has_focus:
            event.stop()
            event.prevent_default()
            self.action_tab_complete()

    @on(Input.Submitted)
    def handle_submit(self):
        self.finish_setup()

    def finish_setup(self):
        profile_mod = self.interface.client.get_module("profile")
        username = self.query_one("#username", Input).value.strip()
        alias = self.query_one("#alias", Input).value.strip()
        
        if not username:
            self.app.notify("Username is required", severity="error")
            return
            
        if profile_mod.create_profile(username=username, alias=alias):
            self.app.notify(f"Profile @{username} created")
            
            self.query_one("#username", Input).value = ""
            self.query_one("#alias", Input).value = ""
            self.query_one("#status_msg", Label).update("")
            
            self.query_one(ContentSwitcher).current = "selector_list"
            self.query_one("#btn_group").display = False
        else:
            self.app.notify("Could not create profile", severity="error")