from velo.services.ollama_client import OllamaClient
from velo.config import AUDIENCE_MODEL, AUDIENCE_PROMPT
from velo.utils.agent_logs import agent as logger
from velo.types.agent import AudienceResearchOut, Message
from velo.agents.tools import get_result, URL_CALLER
from velo.agents.api_connector import WebConnector


class Audience:
    def __init__(self, max_retries: int = 5):
        self.client = OllamaClient(AUDIENCE_MODEL)
        self.system_prompt = Message(
            role="system",
            content=AUDIENCE_PROMPT
        )
        self.output_format = AudienceResearchOut.model_json_schema()
        self.max_retries = max_retries
        self.tools = [
            URL_CALLER
        ]

        web_connector = WebConnector()
        self.tool_callables = {
            URL_CALLER.function.name: web_connector.url_caller
        }

    def generate_profile(self, prompt: str):
        try:
            message = Message(
                role="user",
                content=prompt
            )
            history = [self.system_prompt, message]

            response = self.client.send_with_tools_n_struct(
                history, self.tools, self.output_format
            )
            assert response is not None
            logger.info(
                "agent: %s | model: %s | query_len: %s | resp_dur: %s",
                self.__class__.__name__,
                AUDIENCE_MODEL,
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
                        "parsing %s tool calls from audience LLM",
                        len(response_message.tool_calls)
                    )
                    for call in response_message.tool_calls:
                        history = get_result(
                            self.tool_callables,
                            call,
                            history,
                            logger
                        )
                        response = self.client.send_with_tools_n_struct(
                            history, self.tools, self.output_format
                        )
                        assert response is not None
                        response_message = Message(**response["message"])
                else:
                    tooling = False
            # refocus = """\n\nNow you must ONLY make a tool call to the
            # content_agent. After which you can proceed as normal.
            # """
            return response_message.content
        except Exception as e:
            logger.error(
                "error generating audience profile >> %s",
                e,
                exc_info=True
            )
