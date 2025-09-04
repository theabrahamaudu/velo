from velo.services.ollama_client import OllamaClient
from velo.config import SUPERVISOR_MODEL
from velo.utils.agent_logs import agent as logger
from velo.utils.types import Message


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
