import os

def get_config():
    """Get the appropriate config based on environment."""
    # Check environment variable
    env = os.getenv("APP_ENV", "dev")
    
    # Debug: Print environment (this will show in Streamlit logs)
    print(f"🔍 APP_ENV = {env}")
    
    # If it's prod, use prod config
    if env == "prod":
        from .prod import ProdConfig
        return ProdConfig()
    else:
        from .dev import DevConfig
        return DevConfig()

Config = get_config()