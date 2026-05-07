import json
from typing import Any, Dict
from .base import BaseProcessor
from ..helpers import AIAgentHelper
from ..models import NewsArticle

class JSONProcessor(BaseProcessor):
    def __init__(self, ai_helper: AIAgentHelper):
        self.ai_helper = ai_helper

    async def process(self, json_data: Dict[str, Any], url: str) -> NewsArticle:
        json_str = json.dumps(json_data)
        prompt = f"""
        Extract structured news data from this JSON object.
        Fields: title, summary, date, sentiment.
        JSON: {json_str}
        """
        
        ai_data = await self.ai_helper.reason(prompt)
        ai_data['url'] = url
        return NewsArticle(**ai_data)
