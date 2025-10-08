from velo.services.ollama_client import OllamaClient
from velo.config import SUPERVISOR_MODEL, SUPERVISOR_PROMPT
from velo.utils.agent_logs import agent as logger
from velo.types.agent import Message
from velo.agents.tools import (
    get_result,
    GET_WEATHER,
    URL_CALLER,
    AUDIENCE_TOOL,
    CONTENT_TOOL,
    SCHEDULER_TOOL,
    CREATIVE_TOOL
)
from velo.agents import (
    api_connector,
    audience_agent,
    content_agent,
    scheduler_agent,
    creative_agent
)


class Supervisor:
    def __init__(self, session_id: str, max_retries: int = 10):
        self.client = OllamaClient(SUPERVISOR_MODEL)
        self.system_prompt = Message(
            role="system",
            content=SUPERVISOR_PROMPT
        )
        self.session_id = session_id
        self.max_retries = max_retries
        self.tools = [
            GET_WEATHER,
            URL_CALLER,
            AUDIENCE_TOOL,
            CONTENT_TOOL,
            SCHEDULER_TOOL,
            CREATIVE_TOOL
        ]

        web_connector = api_connector.WebConnector()
        audience = audience_agent.Audience()
        content = content_agent.Content()
        scheduler = scheduler_agent.Scheduler()
        image_generator = creative_agent.Creator()
        self.tool_callables = {
            GET_WEATHER.function.name: web_connector.weather_api,
            URL_CALLER.function.name: web_connector.url_caller,
            AUDIENCE_TOOL.function.name: audience.generate_profile,
            CONTENT_TOOL.function.name: content.generate_content,
            SCHEDULER_TOOL.function.name: scheduler.generate_schedule,
            CREATIVE_TOOL.function.name: image_generator.generate_image
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

    def start_w_tools(self, message: Message, chat_id: int):
        try:
            logger.info(
                "starting campaign generation for prompt `%s`",
                message.content
            )
            history = [self.system_prompt, message]
            response = self.client.send_with_tools(
                history,
                self.tools,
                temperature=0.8
            )
            assert response is not None
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
                    logger.info(
                        "parsing %s tool calls from supervisor LLM",
                        len(response_message.tool_calls)
                    )
                    logger.info(
                        "tool call order >> %s",
                        [call.function.name for call in
                            response_message.tool_calls]
                    )
                    for call in response_message.tool_calls:
                        history = get_result(
                            self.tool_callables,
                            call,
                            history,
                            logger,
                            chat_id
                        )
                        response = self.client.send_with_tools(
                            history,
                            self.tools
                        )
                        assert response is not None
                        response_message = Message(**response["message"])
                else:
                    tooling = False

            return response_message.content[:4000]
        except Exception as e:
            logger.error(
                "error generating campaign >> %s",
                e,
                exc_info=True
            )
