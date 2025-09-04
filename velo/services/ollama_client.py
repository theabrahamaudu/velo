import requests
from velo.config import OLLAMA_URL
from velo.utils.service_logs import service as logger
from velo.utils.types import Message


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
