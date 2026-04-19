"""Shared memory state."""

from typing import Any, Dict

class SharedMemory:
    """
    Runtime KV store.
    """
    def __init__(self):
        self._workspace: Dict[str, Any] = {}

    def get(self, key: str) -> Any:
        return self._workspace.get(key)
    
    def set(self, key: str, value: Any) -> None:
        self._workspace[key] = value

    def exists(self, key: str) -> bool:
        return key in self._workspace

    def clear(self) -> None:
        self._workspace.clear()
    
    def dump(self) -> dict:
        return self._workspace.copy()
