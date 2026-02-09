from typing import Any, Optional

from textual import on
from textual.containers import Center, Horizontal, Middle, Vertical
from textual.events import Key
from textual.widgets import Button, ContentSwitcher, Input, Label, ListItem, ListView

from ..screen import Screen


class ProfileSelector(Screen):
    def __init__(self, interface_instance: Any, **initialization_kwargs: Any) -> None:
        super().__init__(interface_instance, **initialization_kwargs)
        self.current_suggestion: str = ""
        self.validation_timer: Optional[Any] = None

    def compose(self):
        profile_module: Optional[Any] = self.interface.client.get_module("profile")
        profiles_list: list[Any] = profile_module.data.get("profiles", []) if profile_module else []
        
        sorted_profiles: list[Any] = sorted(profiles_list, key=lambda profile_data: profile_data.get("isLastUsed", False), reverse=True)
        
        with Center():
            with Middle():
                with Vertical(id="modal-panel"):
                    with ContentSwitcher(initial="selector-list"):
                        with Vertical(id="selector-list"):
                            yield Label("SELECT PROFILE", classes="title")
                            with ListView(id="profile_list"):
                                for profile_data in sorted_profiles:
                                    profile_username = profile_data["username"]
                                    profile_alias = profile_data.get("social", {}).get("alias", profile_username)
                                    profile_creation_date = profile_data.get("metadata", {}).get("created_at", "N/A")[:10]
                                    is_last_used = profile_data.get("isLastUsed", False)
                                    
                                    with ListItem(id=f"user_{profile_username}"):
                                        with Vertical(classes="card_container"):
                                            with Horizontal():
                                                yield Label(profile_alias, classes="card_alias")
                                                if is_last_used:
                                                    yield Label("LAST USED", classes="last_badge")
                                            
                                            yield Label(f"@{profile_username}", classes="card_username")
                                            yield Label(f"Created: {profile_creation_date}", classes="card_date")
                                
                                with ListItem(id="create_new_trigger"):
                                    with Center():
                                        with Middle():
                                            yield Label("[b]+ Create new profile[/]", id="create_new_label")

                        with Vertical(id="selector_create"):
                            yield Label("CREATE PROFILE", classes="title")
                            yield Input(placeholder="Username (Required)", id="username")
                            yield Label("", id="status_msg")
                            yield Input(placeholder="Alias (Optional)", id="alias")

                    with Center(id="btn_container"):
                        with Horizontal(id="btn_group"):
                            yield Button("Back", id="back_btn")
                            yield Button("Finish", id="next_btn", variant="primary")

    def finish_setup(self) -> None:
        profile_module: Optional[Any] = self.interface.client.get_module("profile")
        username_input_value: str = self.query_one("#username", Input).value.strip()
        alias_input_value: str = self.query_one("#alias", Input).value.strip()
        
        if not username_input_value:
            self.app.notify("Username is required", severity="error")
            return
        
        if not profile_module:
            self.app.notify("Profile module not available", severity="error")
            return
            
        if profile_module.create_profile(username_input_value, alias_input_value):
            self.app.notify(f"Profile @{username_input_value} created")
            
            self.query_one("#username", Input).value = ""
            self.query_one("#alias", Input).value = ""
            self.query_one("#status_msg", Label).update("")
            
            self.query_one(ContentSwitcher).current = "selector-list"
            self.query_one("#btn_group").display = False
        else:
            self.app.notify("Could not create profile", severity="error")

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back_btn":
            self.query_one(ContentSwitcher).current = "selector-list"
            self.query_one("#btn_group").display = False
        elif event.button.id == "next_btn":
            self.finish_setup()

    @on(Input.Submitted)
    def handle_submit(self) -> None:
        self.finish_setup()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "username":
            if self.validation_timer:
                self.validation_timer.stop()
            
            self.query_one("#status_msg", Label).update("")
            self.current_suggestion = ""
            
            self.validation_timer = self.set_timer(0.5, self.validate_username)

    def on_key(self, event: Key) -> None:
        if event.key == "tab" and self.current_suggestion and self.query_one("#username").has_focus:
            event.stop()
            event.prevent_default()
            self.tab_complete()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item.id == "create_new_trigger":
            self.query_one(ContentSwitcher).current = "selector_create"
            self.query_one("#btn_group").display = True
            self.query_one("#username").focus()
        elif event.item.id:
            selected_username: str = event.item.id.replace("user_", "")
            profile_module: Optional[Any] = self.interface.client.get_module("profile")
            if profile_module and profile_module.switch_profile(selected_username):
                self.app.notify(f"Profile @{selected_username} active")

    def on_mount(self) -> None:
        self.query_one("#btn_group").display = False

    def tab_complete(self) -> None:
        username_input: Input = self.query_one("#username", Input)
        if username_input.has_focus and self.current_suggestion:
            username_input.value = self.current_suggestion
            if self.validation_timer:
                self.validation_timer.stop()
            self.validate_username()
            self.query_one("#alias", Input).focus()

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