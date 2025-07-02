from fastapi import APIRouter, HTTPException
from qdrant_client import QdrantClient
from my_agents.config import config

router = APIRouter()

qdrant_client = QdrantClient(
    url=config["databaseClients"]["qdrant"]["url"],
    api_key=config["databaseClients"]["qdrant"]["apiKey"],
    port=config["databaseClients"]["qdrant"]["port"]
)

COLLECTION = "sql_query_cache"

@router.get("/all")
async def get_all_cache():
    try:
        result = qdrant_client.scroll(
            collection_name=COLLECTION,
            limit=100,
        )
        return {
            "success": True,
            "points": result.points
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
