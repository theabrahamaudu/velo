from typing import Dict, List
import requests
from velo.config import OLLAMA_URL
from velo.utils.service_logs import service as logger
from velo.types.agent import Message, Tool


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
            tools: List[Tool],
            temperature: float = 0.5
            ) -> dict | None:
        logger.info("running query with %s model", self.model)
        history_str = [message.model_dump() for message in history]
        tools_str = [tool.model_dump() for tool in tools]
        response = self.session.post(
            url=self.ollama_url+"/api/chat",
            json={
                "model": self.model,
                "messages": history_str,
                "tools": tools_str,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            },
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(
                "error generating response from ollama client >> %s >> %s",
                response.status_code,
                response.raise_for_status(),
                exc_info=True
            )

    def send_with_tools_n_struct(
            self,
            history: List[Message],
            tools: List[Tool],
            output_structure: Dict
            ) -> dict | None:
        logger.info("running query with %s model", self.model)
        history_str = [message.model_dump() for message in history]
        tools_str = [tool.model_dump() for tool in tools]
        response = self.session.post(
            url=self.ollama_url+"/api/chat",
            json={
                "model": self.model,
                "messages": history_str,
                "tools": tools_str,
                "format": output_structure,
                "stream": False
            },
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(
                "error generating response from ollama client >> %s >> %s",
                response.status_code,
                response.raise_for_status(),
                exc_info=True
            )
