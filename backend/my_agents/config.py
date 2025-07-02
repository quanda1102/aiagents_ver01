import os
from dotenv import load_dotenv

load_dotenv(override=True)

def get_env(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise EnvironmentError(f"{name} is required")
    return value

config = {
    "databaseClients": {
        "mysql": {
            "host": get_env("DB_HOST"),
            "port": int(get_env("DB_PORT")),
            "user": get_env("DB_USER"),
            "password": get_env("DB_PASSWORD"),
            "database": get_env("DB_NAME"),
        },
        "qdrant": {
            "url": get_env("QDRANT_URL"),
            "apiKey": get_env("QDRANT_API_KEY"),
            "port": 443,
            "checkCompatibility": False,
            "timeout": 30000,
        },
    },
    "openai": {
        "apiKey": get_env("OPENAI_API_KEY"),
        "timeout": 30000,
    },
    "server": {
        "port": int(os.getenv("PORT", 3000)),
    },
}
