from typing import Any, Dict

class AgentContext:
    def __init__(self, initial_data: Dict[str, Any] = None):
        self._context = initial_data.copy() if initial_data else {}

    def set(self, key: str, value: Any):
        self._context[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._context.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._context)

    def merge(self, other: Dict[str, Any]):
        self._context.update(other)

    def __getitem__(self, key):
        return self._context[key]

    def __setitem__(self, key, value):
        self._context[key] = value

    def __contains__(self, key):
        return key in self._context

    def __repr__(self):
        return f"AgentContext({self._context})"
