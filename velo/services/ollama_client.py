from typing import List
import requests
from velo.config import OLLAMA_URL
from velo.utils.service_logs import service as logger
from velo.utils.types import Message, Tool


class OllamaClient:
    def __init__(self, model: str) -> None:
        self.ollama_url = OLLAMA_URL
        self.model = str(model)
        self.session = requests.Session()

    def send(self, message: Message) -> dict:
        logger.info("running query with %s model", self.model)
        response = self.session.post(
            url=self.ollama_url+"/api/chat",
            json={
                "model": self.model,
                "messages": [{
                    "role": message.role,
                    "content": message.content,
                    "thinking": message.thinking,
                    "images": message.images,
                    "tool_calls": message.tool_calls,
                    "tool_name": message.tool_name
                }],
                "stream": False
            },
            headers={"Content-Type": "application/json"}
        )
        return response.json()

    def send_with_tools(
            self,
            history: List[Message],
            tools: List[Tool]
            ) -> dict:
        logger.info("running query with %s model", self.model)
        history_str = [message.model_dump() for message in history]
        tools_str = [tool.model_dump() for tool in tools]
        response = self.session.post(
            url=self.ollama_url+"/api/chat",
            json={
                "model": self.model,
                "messages": history_str,
                "tools": tools_str,
                "stream": False
            },
            headers={"Content-Type": "application/json"}
        )
        return response.json()
