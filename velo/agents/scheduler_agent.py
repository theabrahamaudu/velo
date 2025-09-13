from velo.services.ollama_client import OllamaClient
from velo.config import SCHEDULER_MODEL, SCHEDULER_PROMPT
from velo.utils.agent_logs import agent as logger
from velo.utils.types import Message, Parameters, Property
from velo.agents.tools import get_result, URL_CALLER
from velo.agents.api_connector import WebConnector


class Scheduler:
    def __init__(self, max_retries: int = 5):
        self.client = OllamaClient(SCHEDULER_MODEL)
        self.system_prompt = Message(
            role="system",
            content=SCHEDULER_PROMPT
        )
        self.output_fromat = Parameters(
            type="object",
            properties={
                "platform": Property(
                    type="array",
                    items={
                        "type": "string"
                    },
                ),
                "datetime": Property(
                    type="array",
                    items={
                        "type": "datetime"
                    },
                ),
                "content_ref": Property(
                    type="array",
                    items={
                        "type": "string"
                    },
                )
            },
            required=["platfrom", "datetime", "content_ref"]
        )
        self.max_retries = max_retries
        self.tools = [
            URL_CALLER
        ]

        web_connector = WebConnector()
        self.tool_callables = {
            URL_CALLER.function.name: web_connector.url_caller
        }

    def generate_schedule(
            self,
            prompt: str,
            ad_copies: str,
            emails: str,
            social_posts: str
            ) -> str:

        context = " using the following >> ad_copies: {} | emails: {} | \
            social_posts: {} << as context".format(
                ad_copies,
                emails,
                social_posts
            )
        message = Message(
            role="user",
            content=prompt + context
        )
        history = [self.system_prompt, message]

        response = self.client.send_with_tools_n_struct(
            history, self.tools, self.output_fromat
        )
        logger.info(
            "agent: %s | model: %s | query_len: %s | resp_dur: %s",
            self.__class__.__name__,
            SCHEDULER_MODEL,
            len(message.content),
            response["total_duration"]
        )
        response_message = Message(**response["message"])

        tooling = True
        count = 0
        while tooling and count < self.max_retries:
            count += 1
            if response_message.tool_calls is not None:
                logger.info("parsing tool calls from scheduler LLM")
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
                    response_message = Message(**response["message"])
            else:
                tooling = False

        return response_message.content
