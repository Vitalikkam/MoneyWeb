class BaseConfig:
    APP_NAME = "Life Dashboard"
    APP_VERSION = "1.0.0"
    ENABLE_FINANCE = True
    ENABLE_FOOD = True
    API_TIMEOUT = 10
    
    def get_env(self):
        raise NotImplementedError