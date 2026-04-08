from typing import Dict, List
import json
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

    def _get_headers(self) -> dict:
        return {
                "Content-Type": "application/json"
            } if self.local else {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
            }

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
            headers=self._get_headers()
        )
        return response.json()

    def send_with_tools(
            self,
            history: List[Message],
            tools: List[Tool],
            temperature: float = 0.5
            ) -> dict | None:
        logger.info("running query with %s model", self.model)
        history_str = [message.to_api_dict() for message in history]
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
            headers=self._get_headers()
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
        history_str = [message.to_api_dict() for message in history]
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
                "stream": False
            },
            headers=self._get_headers()
        )
        print("response text:", response.text)
        if response.status_code == 200:
            response_json = response.json()
            finish_reason = response_json["choices"][0]["finish_reason"]

            if finish_reason == "tool_calls":
                return response_json

            logger.info("attempting to generate structured response")
            schema_instruction = Message(
                role="system",
                content=(
                    "You must respond ONLY with a valid JSON object that "
                    "strictly matches this JSON schema. No explanation, "
                    "no markdown, no code fences:\n"
                    f"{json.dumps(output_structure, indent=2)}"
                )
            )
            response_msg = Message(**response_json["choices"][0]["message"])
            updated_history = [schema_instruction.to_api_dict()] + \
                              [response_msg.to_api_dict()]

            response = self.session.post(
                url=self.llm_url,
                json={
                    "model": self.model,
                    "messages": updated_history,
                    "tools": tools_str,
                    "format": output_structure,
                    "stream": False
                } if self.local else {
                    "model": self.model,
                    "messages": updated_history,
                    # "response_format": {
                    #     "type": "json_schema",
                    #     "json_schema": {
                    #         "name": "structured_response",
                    #         "schema": output_structure
                    #     },
                    # },
                    "stream": False
                },
                headers=self._get_headers()
            )
            if response.status_code == 200:
                logger.info("response structured sucessfully")
                return response.json()
            else:
                logger.error(
                    "error generating structured response from LLM "
                    "client >> %s >> %s",
                    response.status_code,
                    response.text,
                    exc_info=True
                )
        else:
            logger.error(
                "error generating response from LLM client >> %s >> %s",
                response.status_code,
                response.text,
                exc_info=True
            )
