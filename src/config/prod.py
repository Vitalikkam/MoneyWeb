from .base import BaseConfig

class ProdConfig(BaseConfig):
    def get_env(self):
        return "prod"