from velo.services.ollama_client import OllamaClient
from velo.config import SUPERVISOR_MODEL, SUPERVISOR_PROMPT
from velo.utils.agent_logs import agent as logger
from velo.utils.types import Message
from velo.agents.tools import (
    get_result,
    GET_WEATHER,
    URL_CALLER,
    AUDIENCE_TOOL
)
from velo.agents import (
    api_connector,
    audience_agent
)


class Supervisor:
    def __init__(self, max_retries: int = 10):
        self.client = OllamaClient(SUPERVISOR_MODEL)
        self.system_prompt = Message(
            role="system",
            content=SUPERVISOR_PROMPT
        )
        self.max_retries = max_retries
        self.tools = [
            GET_WEATHER,
            URL_CALLER,
            AUDIENCE_TOOL
        ]

        web_connector = api_connector.WebConnector()
        audience = audience_agent.Audience()
        self.tool_callables = {
            GET_WEATHER.function.name: web_connector.weather_api,
            URL_CALLER.function.name: web_connector.url_caller,
            AUDIENCE_TOOL.function.name: audience.generate_profile
        }

    def start(self, message: Message):
        response = self.client.send(message)
        logger.info(
            "agent: %s | model: %s | query_len: %s | resp_dur: %s",
            self.__class__.__name__,
            SUPERVISOR_MODEL,
            len(message.content),
            response["total_duration"]
        )
        return response["message"]["content"]

    def start_w_tools(self, message: Message):
        history = [self.system_prompt, message]

        response = self.client.send_with_tools(history, self.tools)
        logger.info(
            "agent: %s | model: %s | query_len: %s | resp_dur: %s",
            self.__class__.__name__,
            SUPERVISOR_MODEL,
            len(message.content),
            response["total_duration"]
        )
        response_message = Message(**response["message"])

        tooling = True
        count = 0
        while tooling and count < self.max_retries:
            count += 1
            if response_message.tool_calls is not None:
                logger.info("parsing tool calls from supervisor LLM")
                for call in response_message.tool_calls:
                    history = get_result(
                        self.tool_callables,
                        call,
                        history,
                        logger
                    )
                    response = self.client.send_with_tools(history, self.tools)
                    response_message = Message(**response["message"])
            else:
                tooling = False

        return response_message.content
