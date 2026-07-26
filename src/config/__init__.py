import os
from .dev import DevConfig
from .prod import ProdConfig

def get_config():
    """Get the appropriate config based on environment."""
    env = os.getenv("APP_ENV", "dev")
    if env == "prod":
        from .prod import ProdConfig
        return ProdConfig()
    else:
        from .dev import DevConfig
        return DevConfig()

Config = get_config()