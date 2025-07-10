import os
from uuid import uuid4
from datetime import datetime
import ssl
from urllib3.util.ssl_ import create_urllib3_context
from qdrant_client import QdrantClient
from openai import OpenAI
import logging
from dotenv import load_dotenv

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tải biến môi trường từ file .env
load_dotenv(override=True)

class SemanticCacheService:
    def __init__(self):
        # Lấy các biến môi trường
        self.collection_name = os.getenv("QDRANT_COLLECTION_NAME", "sql_query_cache")
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")

        # Kiểm tra các biến môi trường bắt buộc
        if not qdrant_url:
            logger.error("QDRANT_URL is not set in environment variables")
            raise ValueError("QDRANT_URL is required")
        if not qdrant_api_key:
            logger.error("QDRANT_API_KEY is not set in environment variables")
            raise ValueError("QDRANT_API_KEY is required")
        if not openai_api_key:
            logger.error("OPENAI_API_KEY is not set in environment variables")
            raise ValueError("OPENAI_API_KEY is required")

        # Khởi tạo QdrantClient với HTTPS và SSL context
        ssl_context = create_urllib3_context(ssl_version=ssl.PROTOCOL_TLSv1_2)
        self.qdrant_client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
            timeout=30.0,
            prefer_grpc=False,
            https=True,
            ssl_context=ssl_context
        )

        # Khởi tạo OpenAI client
        self.openai = OpenAI(api_key=openai_api_key)

        # Đảm bảo collection tồn tại
        self.ensure_collection()

    def ensure_collection(self):
        """Đảm bảo collection tồn tại trong Qdrant"""
        try:
            self.qdrant_client.get_collection(self.collection_name)
            logger.info(f"Collection {self.collection_name} already exists")
        except Exception as e:
            logger.info(f"Collection {self.collection_name} not found, creating new one")
            try:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config={
                        "size": 1536,
                        "distance": "Cosine"
                    }
                )
                logger.info(f"Created collection {self.collection_name}")
            except Exception as e:
                logger.error(f"Failed to create collection {self.collection_name}: {str(e)}")
                raise

    async def initialize(self):
        """Khởi tạo service (được gọi khi cần)"""
        self.ensure_collection()

    async def get_cached_query(self, question: str):
        """Tìm kiếm câu hỏi trong cache"""
        try:
            self.ensure_collection()

            embedding = self.openai.embeddings.create(
                model="text-embedding-3-small",
                input=question
            ).data[0].embedding

            result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=embedding,
                limit=1,
                score_threshold=0.92,
            )

            if result:
                logger.info(f"Found cached result for question: {question}")
                return result[0].payload
            logger.info(f"No cached result found for question: {question}")
            return None

        except Exception as e:
            logger.error(f"Error searching cache for question '{question}': {str(e)}")
            return None

    async def cache_query(self, question: str, turn_data: dict):
        """Lưu câu hỏi và kết quả vào cache"""
        try:
            self.ensure_collection()

            embedding = self.openai.embeddings.create(
                model="text-embedding-3-small",
                input=question
            ).data[0].embedding

            self.qdrant_client.upsert(
                collection_name=self.collection_name,
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
                }],
                wait=True
            )
            logger.info(f"Successfully cached query: {question}")

        except Exception as e:
            logger.error(f"Error caching query '{question}': {str(e)}")