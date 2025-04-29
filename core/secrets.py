# core/secrets.py

import json
import os

class SecretsManager:
    """
    Simple secrets manager for local development.
    Loads secrets from .secrets.json at the project root.
    TODO: Use a more secure method for production (e.g., AWS Secrets Manager, Azure Key Vault).
    This is a simple implementation for local development only.
    """

    def __init__(self):
        self.secrets = self._load_secrets()

    def _load_secrets(self) -> dict:
        path = ".secrets.json"
        if not os.path.exists(path):
            raise FileNotFoundError("No .secrets.json file found at the project root.")

        with open(path, "r") as f:
            return json.load(f)

    def get(self, key: str) -> str:
        """Get a secret value by key."""
        return self.secrets.get(key)

    def all(self) -> dict:
        """Get all secrets (use carefully)."""
        return self.secrets
