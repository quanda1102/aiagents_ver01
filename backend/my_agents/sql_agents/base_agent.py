import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

from my_agents.services.conversation_history_service import ConversationHistoryService
from my_agents.services.semantic_cache_service import SemanticCacheService

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    name: str = "UnnamedAgent"
    role: str = "GenericAgent"

    async def process(self, input_data: Any, context: Dict[str, Any]) -> Any:
        logger.info(f"[{self.name}] Input: {input_data}")

        try:
            result = await self.run(input_data, context)
            logger.info(f"[{self.name}] Output: {result}")
        except Exception as e:
            logger.exception(f"[{self.name}] Error during processing")
            raise e

        if context.get("sessionId"):
            self.save_history(context["sessionId"], {
                "agent": self.name,
                "role": self.role,
                "input": input_data,
                "output": result,
            })

        if context.get("cache") is True:
            await self.cache_response(input_data, result)

        return result

    def save_history(self, session_id: str, turn_data: Dict[str, Any]):
        ConversationHistoryService.save_turn(session_id, turn_data)

    async def cache_response(self, input_data: Any, result: Any):
        try:
            await SemanticCacheService.cache_query(str(input_data), result)
        except Exception as e:
            logger.warning(f"[{self.name}] Failed to cache response: {e}")

    @abstractmethod
    async def run(self, input_data: Any, context: Dict[str, Any]) -> Any:
        pass
