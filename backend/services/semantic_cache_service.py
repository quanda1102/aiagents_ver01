import uuid
import logging
import json
from typing import Optional, List, Dict, Any
from decimal import Decimal

from qdrant_client import QdrantClient, models
from openai import AsyncOpenAI
from my_agents.config import config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticCacheService:
    def __init__(self):
        try:
            qdrant_config = config['qdrant']
            self.client = QdrantClient(
                url=qdrant_config['url'],
                api_key=qdrant_config['api_key'],
                timeout=30.0,
                prefer_grpc=False
            )
            self.collection_name = qdrant_config['collection_name']
            self.embedding_model = "text-embedding-3-small"
            self.vector_size = 1536
            self.openai_client = AsyncOpenAI(api_key=config["openai"]["api_key"])

            self.setup_collection()
            logger.info(f"✅ Đã kết nối Qdrant collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"❌ Lỗi khi khởi tạo SemanticCacheService: {e}")
            self.client = None

    def setup_collection(self):
        try:
            collections_response = self.client.get_collections()
            existing = [c.name for c in collections_response.collections]
            if self.collection_name not in existing:
                self.client.recreate_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"📦 Tạo collection mới: {self.collection_name}")
        except Exception as e:
            logger.error(f"❌ Lỗi khi thiết lập collection: {e}")

    async def get_embedding(self, text: str) -> Optional[List[float]]:
        try:
            text = text.replace("\n", " ")
            response = await self.openai_client.embeddings.create(
                input=[text],
                model=self.embedding_model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"❌ Lỗi khi tạo embedding: {e}")
            return None

    async def search_cache(self, question: str, similarity_threshold: float = 0.95) -> Optional[Dict[str, Any]]:
        question_vector = await self.get_embedding(question)
        if not question_vector:
            return None

        try:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=question_vector,
                limit=1,
                score_threshold=similarity_threshold
            )

            if search_result:
                hit = search_result[0]
                logger.info(f"🔍 Tìm thấy kết quả với score {hit.score:.4f} cho: '{question}'")
                return {
                    "final_response": hit.payload.get("final_response"),
                    "cached": True,
                    "debug_info": hit.payload.get("debug_info")
                }

            logger.info(f"❌ Không tìm thấy kết quả phù hợp trong cache cho: '{question}'")
            return None
        except Exception as e:
            logger.error(f"❌ Lỗi khi tìm kiếm cache: {e}")
            return None

    async def add_to_cache(self, question: str, final_response: str, debug_info: Dict[str, Any]):
        question_vector = await self.get_embedding(question)
        if not question_vector:
            return

        # Chuyển Decimal -> str để tránh lỗi JSON encode
        def clean_debug_info(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            if isinstance(obj, dict):
                return {k: clean_debug_info(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [clean_debug_info(i) for i in obj]
            return obj

        cleaned_debug_info = clean_debug_info(debug_info)

        point_id = str(uuid.uuid4())
        payload = {
            "original_question": question,
            "final_response": final_response,
            "debug_info": cleaned_debug_info,
        }

        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector=question_vector,
                        payload=payload
                    )
                ],
                wait=True
            )
            logger.info(f"✅ Đã thêm vào cache: '{question}'")
        except Exception as e:
            logger.error(f"❌ Lỗi khi thêm vào cache: {e}")
