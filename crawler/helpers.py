import httpx
import json
import asyncio
from typing import Any, Dict

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
                return json.loads(result['response'])
        except Exception as e:
            self._failure_count += 1
            if self._failure_count > 3:
                self._circuit_open = True
                self._last_failure_time = asyncio.get_event_loop().time()
            raise Exception(f"AI Reasoning failed: {str(e)}")
