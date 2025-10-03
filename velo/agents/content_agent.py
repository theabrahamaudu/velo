from velo.services.ollama_client import OllamaClient
from velo.config import CONTENT_MODEL, CONTENT_PROMPT
from velo.utils.agent_logs import agent as logger
from velo.utils.types import Message, Parameters, Property
from velo.agents.tools import get_result, URL_CALLER
from velo.agents.api_connector import WebConnector


class Content:
    def __init__(self, max_retries: int = 5):
        self.client = OllamaClient(CONTENT_MODEL)
        self.system_prompt = Message(
            role="system",
            content=CONTENT_PROMPT
        )
        self.output_fromat = Parameters(
            type="object",
            properties={
                "ad_copies": Property(
                    type="array",
                    items={
                        "type": "string"
                    },
                    description="maximum of two items"
                ),
                "emails": Property(
                    type="array",
                    items={
                        "type": "string"
                    },
                    description="maximum of two items"
                ),
                "social_posts": Property(
                    type="array",
                    items={
                        "type": "string"
                    },
                    description="maximum of two items"
                )
            },
            required=["ad_copies", "emails", "social_posts"]
        )
        self.max_retries = max_retries
        self.tools = [
            URL_CALLER
        ]

        web_connector = WebConnector()
        self.tool_callables = {
            URL_CALLER.function.name: web_connector.url_caller
        }

    def generate_content(
            self,
            prompt: str,
            keywords: str,
            interests: str,
            pain_points: str
            ) -> str | None:
        try:
            context = " using the following >> keywords: {} | interests: {} | \
                pain points: {} << as context".format(
                    keywords,
                    interests,
                    pain_points
                )
            message = Message(
                role="user",
                content=prompt + context
            )
            history = [self.system_prompt, message]

            response = self.client.send_with_tools_n_struct(
                history, self.tools, self.output_fromat
            )
            assert response is not None
            logger.info(
                "agent: %s | model: %s | query_len: %s | resp_dur: %s",
                self.__class__.__name__,
                CONTENT_MODEL,
                len(message.content),
                response["total_duration"]
            )
            response_message = Message(**response["message"])

            tooling = True
            count = 0
            while tooling and count < self.max_retries:
                count += 1
                if response_message.tool_calls is not None:
                    logger.info("parsing tool calls from content LLM")
                    for call in response_message.tool_calls:
                        history = get_result(
                            self.tool_callables,
                            call,
                            history,
                            logger
                        )
                        response = self.client.send_with_tools_n_struct(
                            history, self.tools, self.output_fromat
                        )
                        assert response is not None
                        response_message = Message(**response["message"])
                else:
                    tooling = False

            return response_message.content
        except Exception as e:
            logger.error(
                "error generating content copies >> %s",
                e,
                exc_info=True
            )
