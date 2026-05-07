import httpx
from typing import Any, Dict, Union
from .interfaces import ScrapingStrategy

class StaticScrapingStrategy(ScrapingStrategy):
    async def scrape(self, url: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

class APIScrapingStrategy(ScrapingStrategy):
    async def scrape(self, url: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
