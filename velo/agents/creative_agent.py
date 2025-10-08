import os
import base64
from velo.services.sd_client import SDClient
from velo.config import CREATIVE_MODEL, CREATIVES_PATH
from velo.utils.agent_logs import agent as logger
from velo.types.agent import SDMessage
from time import perf_counter_ns
from datetime import datetime


class Creator:
    def __init__(self, max_retries: int = 5):
        self.client = SDClient(CREATIVE_MODEL)
        self.save_folder = CREATIVES_PATH
        self.max_retries = max_retries

    def generate_image(
            self,
            prompt: str,
            negative_prompt: str,
            chat_id: str) -> str | None:

        try:
            message = SDMessage(
                prompt=prompt,
                negative_prompt=negative_prompt
            )

            start = perf_counter_ns()
            response = self.client.send(
                message
            )
            total_dur = perf_counter_ns() - start

            logger.info(
                "agent: %s | model: %s | query_len: %s | resp_dur: %s",
                self.__class__.__name__,
                CREATIVE_MODEL,
                len(message.prompt),
                total_dur
            )

            if response is not None:
                response_images = response["images"]

            img_paths = []
            time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
            self.clear_save_path(chat_id)
            for idx, img in enumerate(response_images):
                img_bytes = base64.b64decode(img)
                img_path = self.save_image(
                    img_bytes,
                    idx,
                    chat_id,
                    time
                )
                img_paths.append(img_path)

            return str(img_paths)
        except Exception as e:
            logger.error(
                "error generating images >> %s",
                e,
                exc_info=True
            )

    def save_image(
            self,
            image_bytes: bytes,
            idx: int,
            chat_id: str,
            timestamp: str) -> str | None:
        try:
            save_path = f"{self.save_folder}/{chat_id}"
            os.makedirs(save_path, exist_ok=True)

            img_path = os.path.join(
                save_path,
                f"output_{timestamp}_{idx+1}.png"
            )
            with open(img_path, "wb") as f:
                f.write(image_bytes)
            logger.info("saved image to %s", img_path)

            return img_path
        except Exception as e:
            logger.error(
                "error saving image to file >> %s",
                e,
                exc_info=True
            )

    def clear_save_path(self, chat_id: str):
        try:
            save_path = f"{self.save_folder}/{chat_id}"
            for filename in os.listdir(save_path):
                if filename.endswith(".png"):
                    os.remove(save_path+"/"+filename)
        except Exception as e:
            logger.error(
                "error clearing save file path >> %s",
                e,
                exc_info=True
            )
