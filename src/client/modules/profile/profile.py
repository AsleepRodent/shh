import json
import random
from pathlib import Path
from datetime import datetime
import coolname
from ..module import Module

class Profile(Module):
    def __init__(self, client, directory):
        super().__init__("Profile", client)
        self.directory = Path(directory)
        self.path = self.directory / ".shh" / "userdata.json"
        self.data = self.load()
        self.selected_profile = None

    def load(self):
        default = {"profiles": [], "global": {"first_run": True}}
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.save(default)
            return default
        with open(self.path, "r") as reader:
            return json.load(reader)

    def save(self, data=None):
        target_data = data if data else self.data
        with open(self.path, "w") as writer:
            json.dump(target_data, writer, indent=4)

    def switch_profile(self, username):
        found = False
        for profile in self.data["profiles"]:
            if profile["username"].lower() == username.lower().strip():
                profile["isLastUsed"] = True
                self.selected_profile = profile
                found = True
            else:
                profile["isLastUsed"] = False
        
        if found:
            self.save()
        return found

    def exists(self, username):
        return any(p["username"].lower() == username.lower().strip() for p in self.data["profiles"])

    def suggest_username(self, username):
        base = username.lower().strip()
        while True:
            cool = coolname.generate_slug(2) # type: ignore
            word = cool.split('-')[0]
            strategies = [f"{base}_{word}", f"{word}.{base}", f"{base}-{random.randint(10, 99)}", f"{cool}"]
            suggestion = random.choice(strategies)
            if not self.exists(suggestion):
                return suggestion

    def create_profile(self, username, alias):
        if self.exists(username):
            return False
        
        for profile in self.data["profiles"]:
            profile["isLastUsed"] = False

        new_profile = {
            "index": len(self.data["profiles"]) + 1,
            "isLastUsed": True,
            "username": username.strip(),
            "metadata": {"created_at": datetime.now().isoformat(), "status": "active"},
            "social": {
                "alias": alias.strip() if alias.strip() else username.strip(),
                "verified": False
            }
        }
        self.data["profiles"].append(new_profile)
        self.data["global"]["first_run"] = False
        self.selected_profile = new_profile
        self.save()
        return True