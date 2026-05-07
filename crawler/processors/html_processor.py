from bs4 import BeautifulSoup
from .base import BaseProcessor
from ..helpers import AIAgentHelper
from ..models import NewsArticle

class HTMLDomProcessor(BaseProcessor):
    def __init__(self, ai_helper: AIAgentHelper):
        self.ai_helper = ai_helper

    async def process(self, html_content: str, url: str) -> NewsArticle:
        soup = BeautifulSoup(html_content, 'html.parser')
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
        
        clean_text = soup.get_text(separator=' ', strip=True)[:4000]
        
        prompt = f"""
        Extract structured news data from the following text in JSON format.
        Fields: title, summary, date, sentiment.
        Text: {clean_text}
        """
        
        ai_data = await self.ai_helper.reason(prompt)
        ai_data['url'] = url
        return NewsArticle(**ai_data)
