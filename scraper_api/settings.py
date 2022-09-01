"""Class to manage the settings, env variables and secrets.
"""

import logging
import os
import sys

from dotenv import load_dotenv

from scraper_api.secrets.keys import DEV_KEYS

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
log = logging.getLogger(__name__)


ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev").lower()


class Settings:
    RUNNING_LOCAL = os.environ.get("RUNNING_LOCAL", False)

    def __init__(self, ENV: str):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.SECRETS_DIR = os.path.join(self.BASE_DIR, "secrets")
        self.FILES_DIR = os.path.join(self.BASE_DIR, "files")
        self.ENV = ENV

        self._get_secrets()
        if ENV == "dev":
            self._get_dev_keys()

    def _get_secrets(self):
        """Open the .env file if it exists or try to get the secrets from Secret Manager

        Raises:
            Exception: if secrets were not found
        """
        env_file = os.path.join(self.SECRETS_DIR, ".env")

        if os.path.isfile(env_file):
            load_dotenv(env_file)
        else:
            raise Exception("No local .env detected. No secrets found.")

    def _get_dev_keys(self):
        """Get access keys for testing and devs"""
        self.DEV_KEYS = DEV_KEYS


class Development(Settings):
    ENV_LOCAL = True
    DOWNLOAD_BUCKET_FILES = True
    WRITE_INTERMEDIATE_FILES = True


class Staging(Settings):
    ENV_LOCAL = False
    DOWNLOAD_BUCKET_FILES = False
    WRITE_INTERMEDIATE_FILES = False
    logging.getLogger().setLevel(logging.INFO)


class Production(Settings):
    ENV_LOCAL = False
    DOWNLOAD_BUCKET_FILES = False
    WRITE_INTERMEDIATE_FILES = False
    logging.getLogger().setLevel(logging.INFO)


settings_dict = {
    "dev": Development,
    "staging": Staging,
    "production": Production,
}

settings = settings_dict[ENVIRONMENT](ENV=ENVIRONMENT)

log.info(f"Using environment: {settings.ENV} ")
