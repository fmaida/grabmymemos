from pathlib import Path
import requests


class ConfigClass:
    def __init__(self, base_url: str, token: str | Path):
        self.force_a_title = False
        self.wrap_titles_at = -1
        self.base_url = base_url
        self.session = requests.Session()
        self.last_fetched_page = None
        self.token = token  # chiama il setter

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, valore: str | Path):
        if isinstance(valore, Path):
            valore = valore.read_text(encoding="utf-8").strip()
        self._token = valore
        self.session.headers.update({"Authorization": f"Bearer {valore}"})
