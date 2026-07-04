import os
from .dev import DevConfig
from .prod import ProdConfig

def get_config():
    env = os.getenv("APP_ENV", "dev")
    if env == "prod":
        return ProdConfig()
    return DevConfig()

Config = get_config()