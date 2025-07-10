import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path, override=True)

config = {
    "server": {
        "port": os.getenv("PORT", 8000)
    },
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY")
    },
    "databaseClients": {
        "mysql": {
            "host": os.getenv("DB_HOST"),
            "port": int(os.getenv("DB_PORT", 3306)),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "database": os.getenv("DB_NAME")
        }
    },
    "qdrant": {
        "url": os.getenv("QDRANT_URL"),
        "api_key": os.getenv("QDRANT_API_KEY"),
        "collection_name": "sql_query_cache"
    },
    "redis": {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", 6379)),
        "password": os.getenv("REDIS_PASSWORD")
    }
    
}