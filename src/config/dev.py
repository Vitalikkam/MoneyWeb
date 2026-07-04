from .base import BaseConfig

class DevConfig(BaseConfig):
    def get_env(self):
        return "dev"