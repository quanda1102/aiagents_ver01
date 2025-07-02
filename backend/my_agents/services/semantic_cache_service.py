from uuid import uuid4
from datetime import datetime
from openai import OpenAI
from qdrant_client import QdrantClient
from my_agents.config import config

class SemanticCacheService:
    COLLECTION_NAME = "sql_query_cache"

    qdrant_client = QdrantClient(
        url=config["databaseClients"]["qdrant"]["url"],
        api_key=config["databaseClients"]["qdrant"]["apiKey"],
        port=config["databaseClients"]["qdrant"]["port"],
    )

    openai = OpenAI(api_key=config["openai"]["apiKey"])

    @classmethod
    def ensure_collection(cls):
        try:
            try:
                cls.qdrant_client.get_collection(cls.COLLECTION_NAME)
            except:
                cls.qdrant_client.create_collection(
                    collection_name=cls.COLLECTION_NAME,
                    vectors_config={
                        "size": 1536,
                        "distance": "Cosine"
                    }
                )
                print(f"Created collection {cls.COLLECTION_NAME}")
        except Exception as e:
            print("Failed to ensure collection:", e)
            raise

    @classmethod
    async def initialize(cls):
        cls.ensure_collection()

    @classmethod
    async def get_cached_query(cls, question: str):
        cls.ensure_collection()

        embedding = cls.openai.embeddings.create(
            model="text-embedding-3-small",
            input=question
        ).data[0].embedding

        result = cls.qdrant_client.search(
            collection_name=cls.COLLECTION_NAME,
            query_vector=embedding,
            limit=1,
            score_threshold=0.92,
        )

        return result[0].payload if result else None

    @classmethod
    async def cache_query(cls, question: str, turn_data: dict):
        cls.ensure_collection()

        embedding = cls.openai.embeddings.create(
            model="text-embedding-3-small",
            input=question
        ).data[0].embedding

        cls.qdrant_client.upsert(
            collection_name=cls.COLLECTION_NAME,
            points=[{
                "id": str(uuid4()),
                "vector": embedding,
                "payload": {
                    "question": question,
                    "intent": turn_data.get("intent"),
                    "schema": turn_data.get("schema"),
                    "probes": turn_data.get("probes"),
                    "sql": turn_data.get("sql", {}).get("sql"),
                    "reasoning": turn_data.get("sql", {}).get("reasoning"),
                    "confidence": turn_data.get("sql", {}).get("confidence"),
                    "validation": turn_data.get("validation"),
                    "explanation": turn_data.get("explanation"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {
                        "source": "text-to-sql",
                        "database": turn_data.get("sql", {}).get("database", "unknown")
                    }
                }
            }]
        )
