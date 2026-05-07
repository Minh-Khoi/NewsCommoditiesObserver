from abc import ABC, abstractmethod
from typing import Any

class BaseProcessor(ABC):
    @abstractmethod
    async def process(self, data: Any, url: str) -> Any:
        pass
