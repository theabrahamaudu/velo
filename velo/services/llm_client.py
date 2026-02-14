from typing import Dict, List
import requests
from velo.config import (
    OLLAMA_URL,
    DEEPSEEK_URL,
    DEEPSEEK_API_KEY,
    DEEPSEEK_MODEL_NAME,
    LOCAL_INFERENCE
)
from velo.utils.service_logs import service as logger
from velo.types.agent import Message, Tool


class LLMClient:
    def __init__(self, model: str) -> None:
        self.local = LOCAL_INFERENCE
        if self.local:
            self.llm_url = OLLAMA_URL
            self.model = str(model)
        else:
            self.llm_url = DEEPSEEK_URL
            self.model = DEEPSEEK_MODEL_NAME
        self.session = requests.Session()

    def send(self, message: Message) -> dict:
        logger.info("running query with %s model", self.model)
        response = self.session.post(
            url=self.llm_url,
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
            headers={
                "Content-Type": "application/json"
            } if self.local else {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
            }
        )
        return response.json()

    def send_with_tools(
            self,
            history: List[Message],
            tools: List[Tool],
            temperature: float = 0.5
            ) -> dict | None:
        logger.info("running query with %s model", self.model)
        history_str = [
            message.model_dump(exclude_none=True) for message in history
        ]
        tools_str = [tool.model_dump(exclude_none=True) for tool in tools]
        response = self.session.post(
            url=self.llm_url,
            json={
                "model": self.model,
                "messages": history_str,
                "tools": tools_str,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            },
            headers={"Content-Type": "application/json"} if self.local else {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
            }
        )
        print("response text:", response.text)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(
                "error generating response from LLM client >> %s >> %s",
                response.status_code,
                response.text,
                exc_info=True
            )

    def send_with_tools_n_struct(
            self,
            history: List[Message],
            tools: List[Tool],
            output_structure: Dict
            ) -> dict | None:
        logger.info("running query with %s model", self.model)
        history_str = [
            message.model_dump(exclude_none=True) for message in history
        ]
        tools_str = [tool.model_dump(exclude_none=True) for tool in tools]
        response = self.session.post(
            url=self.llm_url,
            json={
                "model": self.model,
                "messages": history_str,
                "tools": tools_str,
                "format": output_structure,
                "stream": False
            } if self.local else {
                "model": self.model,
                "messages": history_str,
                "tools": tools_str,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "weather_response",
                        "schema": output_structure
                    },
                },
                "stream": False
            },
            headers={
                "Content-Type": "application/json"
            } if self.local else {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
            }
        )
        print("response text:", response.text)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(
                "error generating response from LLM client >> %s >> %s",
                response.status_code,
                response.text,
                exc_info=True
            )
