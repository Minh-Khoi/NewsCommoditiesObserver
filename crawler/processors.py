import httpx
import json
import asyncio
from typing import Any, Dict
from bs4 import BeautifulSoup
from .interfaces import BaseProcessor
from .models import NewsArticle

class AIAgentHelper:
    """Helper to interact with local Ollama LLM."""
    def __init__(self, model: str = "deepseek-r1:1.5b", timeout: float = 30.0):
        self.model = model
        self.timeout = timeout
        self.ollama_url = "http://localhost:11434/api/generate"
        self._failure_count = 0
        self._circuit_open = False
        self._last_failure_time = 0

    async def _check_circuit(self):
        if self._circuit_open:
            if asyncio.get_event_loop().time() - self._last_failure_time > 60:
                self._circuit_open = False
                self._failure_count = 0
            else:
                raise Exception("Circuit Breaker is OPEN. Ollama server is likely overloaded.")

    async def reason(self, prompt: str) -> Dict[str, Any]:
        await self._check_circuit()
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.ollama_url, json=payload)
                response.raise_for_status()
                result = response.json()
                # Assuming Ollama returns a JSON string in 'response' field when format='json'
                return json.loads(result['response'])
        except Exception as e:
            self._failure_count += 1
            if self._failure_count > 3:
                self._circuit_open = True
                self._last_failure_time = asyncio.get_event_loop().time()
            raise Exception(f"AI Reasoning failed: {str(e)}")

class HTMLDomProcessor(BaseProcessor):
    def __init__(self, ai_helper: AIAgentHelper):
        self.ai_helper = ai_helper

    async def process(self, html_content: str, url: str) -> NewsArticle:
        soup = BeautifulSoup(html_content, 'html.parser')
        # Basic cleanup: remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
        
        clean_text = soup.get_text(separator=' ', strip=True)[:4000] # Limit context for small model
        
        prompt = f"""
        Extract structured news data from the following text in JSON format.
        Fields: title, summary, date, sentiment.
        Text: {clean_text}
        """
        
        ai_data = await self.ai_helper.reason(prompt)
        ai_data['url'] = url
        return NewsArticle(**ai_data)

class JSONProcessor(BaseProcessor):
    def __init__(self, ai_helper: AIAgentHelper):
        self.ai_helper = ai_helper

    async def process(self, json_data: Dict[str, Any], url: str) -> NewsArticle:
        # Prompt 1 says JSONProcessor uses AIAgentHelper for LLM reasoning too
        # but Prompt 2 suggests direct field mapping. 
        # I'll implement a hybrid: Try direct mapping first, then AI if it's complex, 
        # or just follow Prompt 1's latest instruction.
        
        # Let's assume we use AI to summarize or extract sentiment even from JSON 
        # if the fields aren't perfectly aligned.
        
        json_str = json.dumps(json_data)
        prompt = f"""
        Extract structured news data from this JSON object.
        Fields: title, summary, date, sentiment.
        JSON: {json_str}
        """
        
        ai_data = await self.ai_helper.reason(prompt)
        ai_data['url'] = url
        return NewsArticle(**ai_data)
