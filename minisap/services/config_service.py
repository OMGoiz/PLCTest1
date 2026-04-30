import json
from pathlib import Path


class ConfigService:
    def __init__(self, path: Path):
        self.path = path
        self.data = self._load()

    def _load(self):
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def reload(self):
        self.data = self._load()

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)
