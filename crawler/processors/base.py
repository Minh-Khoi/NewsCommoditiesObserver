from abc import ABC, abstractmethod
from typing import Any, Optional
from ..helpers import AIAgentHelper

class BaseProcessor(ABC):
    def __init__(self, ai_helper: Optional[AIAgentHelper] = None):
        self.ai_helper = ai_helper

    @abstractmethod
    async def process(self, data: Any, url: str) -> Any:
        pass
