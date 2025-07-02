from typing import Any, Dict
from my_agents.services.semantic_cache_service import SemanticCacheService

class AgentCommunication:
    @staticmethod
    async def query_cache_or_execute(question: str, context: Dict[str, Any], agent) -> Any:
        """
        Nếu không skip cache, thử lấy từ semantic cache.
        Nếu không có, gọi agent và lưu lại cache.
        """
        if context.get("skipCache"):
            return await agent.process(question, context)

        cached = await SemanticCacheService.get_cached_query(question)
        if cached:
            return cached

        result = await agent.process(question, context)
        context["cache"] = True
        await SemanticCacheService.cache_query(question, result)
        return result
