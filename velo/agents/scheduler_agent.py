from velo.services.llm_client import LLMClient
from velo.config import SCHEDULER_MODEL, SCHEDULER_PROMPT, MAX_RETRIES
from velo.utils.agent_logs import agent as logger
from velo.types.agent import Message, ScheduleGenOut
from velo.agents.tools import get_result, URL_CALLER, WEB_SEARCH
from velo.agents.api_connector import WebConnector


class Scheduler:
    def __init__(self, max_retries: int = MAX_RETRIES):
        self.client = LLMClient(SCHEDULER_MODEL)
        self.system_prompt = Message(
            role="system",
            content=SCHEDULER_PROMPT
        )
        self.output_format = ScheduleGenOut.model_json_schema()
        self.max_retries = max_retries
        self.tools = [
            URL_CALLER,
            WEB_SEARCH
        ]

        web_connector = WebConnector()
        self.tool_callables = {
            URL_CALLER.function.name: web_connector.url_caller,
            WEB_SEARCH.function.name: web_connector.web_search_engine
        }

    def generate_schedule(
            self,
            prompt: str,
            ad_copies: str,
            emails: str,
            social_posts: str,
            campaign_id: int
            ) -> str | None:
        try:
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
                history, [], self.output_format
            )
            assert response is not None
            logger.info(
                "agent: %s | model: %s | query_len: %s | resp_dur: %s",
                self.__class__.__name__,
                SCHEDULER_MODEL,
                len(message.content),
                response[
                    "total_duration"
                ] if "total_duration" in response.keys() else "Not Available"
            )
            try:
                response_message = Message(**response["message"])
            except Exception:
                response_message = Message(**response["choices"][0]["message"])

            tooling = True
            count = 0
            while tooling and count < self.max_retries:
                count += 1
                if response_message.tool_calls is not None:
                    logger.info(
                        "parsing %s tool calls from scheduler LLM",
                        len(response_message.tool_calls)
                    )

                    history.append(response_message)

                    for call in response_message.tool_calls:
                        history = get_result(
                            self.tool_callables,
                            call,
                            history,
                            logger,
                            campaign_id
                        )
                        response = self.client.send_with_tools_n_struct(
                            history, [], self.output_format
                        )
                        assert response is not None
                        if self.client.local:
                            response_message = Message(**response["message"])
                        else:
                            response_message = Message(
                                **response["choices"][0]["message"]
                            )
                else:
                    tooling = False

            return response_message.content
        except Exception as e:
            logger.error(
                "error generating content schedule >> %s",
                e,
                exc_info=True
            )
