from velo.services.ollama_client import OllamaClient
from velo.config import SUPERVISOR_MODEL
from velo.utils.agent_logs import agent as logger
from velo.utils.types import Message
from velo.agents.api_connector import GET_WEATHER, WebConnector


class Supervisor:
    def __init__(self):
        self.client = OllamaClient(SUPERVISOR_MODEL)

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
        history = [message]
        tools = [GET_WEATHER]
        response = self.client.send_with_tools(history, tools)
        logger.info(
            "agent: %s | model: %s | query_len: %s | resp_dur: %s",
            self.__class__.__name__,
            SUPERVISOR_MODEL,
            len(message.content),
            response["total_duration"]
        )
        response_message = Message(**response["message"])
        if len(response_message.tool_calls) != 0:  # type: ignore
            logger.info("parsing tool calls from LLM")
            for call in response_message.tool_calls:  # type: ignore
                if call.function.name == "weather_api":
                    logger.info("using tool: %s", GET_WEATHER.model_dump())
                    result = WebConnector().weather_api(
                        call.function.arguments["city"]
                    )
                    history.append(
                        Message(
                            role="tool",
                            content=result,
                            tool_name="weather_api"
                        )
                    )
                    response = self.client.send_with_tools(history, tools)
                    response_message = Message(**response["message"])

        return response_message.content
