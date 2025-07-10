from fastapi import APIRouter, HTTPException
from qdrant_client import QdrantClient
from my_agents.config import config

router = APIRouter()

# Cấu hình lại QdrantClient tương thích HTTPS
qdrant_client = QdrantClient(
    url=config["qdrant"]["url"],
    api_key=config["qdrant"]["api_key"],
    timeout=30.0,
    prefer_grpc=False
)

COLLECTION = config["qdrant"]["collection_name"]

@router.get("/all")
async def get_all_cache():
    try:
        result = qdrant_client.scroll(
            collection_name=COLLECTION,
            limit=100,
        )
        return {
            "success": True,
            "points": result[0]  # result là Tuple[List[ScoredPoint], Optional[int]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear")
async def clear_cache():
    try:
        qdrant_client.delete_collection(collection_name=COLLECTION)
        return {
            "success": True,
            "message": "Cache cleared"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
