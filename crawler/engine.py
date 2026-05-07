import asyncio
from typing import Dict, Type
from .interfaces import ScrapingStrategy
from .strategies import StaticScrapingStrategy, APIScrapingStrategy
from .processors import BaseProcessor, HTMLDomProcessor, JSONProcessor
from .helpers import AIAgentHelper

class CrawlerContext:
    def __init__(self, ai_concurrency_limit: int = 2):
        self.ai_semaphore = asyncio.Semaphore(ai_concurrency_limit)
        self.ai_helper = AIAgentHelper()
        
        self._strategies: Dict[str, ScrapingStrategy] = {}
        self._processors: Dict[Type[ScrapingStrategy], BaseProcessor] = {}

        # Default Registration
        self.register_strategy("static", StaticScrapingStrategy(), HTMLDomProcessor(self.ai_helper))
        self.register_strategy("api", APIScrapingStrategy(), JSONProcessor(self.ai_helper))

    def register_strategy(self, name: str, strategy: ScrapingStrategy, processor: BaseProcessor):
        """Allows adding new strategies without modifying the core engine."""
        self._strategies[name] = strategy
        self._processors[type(strategy)] = processor

    def _get_strategy_key(self, url: str) -> str:
        if "/api/" in url or url.endswith(".json"):
            return "api"
        return "static"

    async def crawl_and_process(self, url: str):
        key = self._get_strategy_key(url)
        strategy = self._strategies.get(key)
        if not strategy:
            raise ValueError(f"No strategy registered for key: {key}")
            
        processor = self._processors[type(strategy)]

        # Step 1: Scrape
        data = await strategy.scrape(url)

        # Step 2: Process (with AI concurrency limit)
        async with self.ai_semaphore:
            article = await processor.process(data, url)
            return article
