from abc import ABC, abstractmethod
from typing import Any, Dict, Union

class ScrapingStrategy(ABC):
    @abstractmethod
    async def scrape(self, url: str) -> Union[str, Dict[str, Any]]:
        pass

class BaseProcessor(ABC):
    @abstractmethod
    async def process(self, data: Any, url: str) -> Any:
        pass
