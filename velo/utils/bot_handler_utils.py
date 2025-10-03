import os
from telegram import InputMediaPhoto
from velo.config import CREATIVES_PATH
from velo.utils.service_logs import service as logger


def load_images(chat_id: str) -> list[InputMediaPhoto] | None:
    base_path = CREATIVES_PATH+"/"+chat_id
    try:
        image_paths = []
        for filename in os.listdir(base_path):
            if filename.endswith(".png"):
                image_paths.append(filename)

        images = []
        for idx, image_path in enumerate(image_paths):
            images.append(
                InputMediaPhoto(
                    open(base_path+"/"+image_path, "rb"),
                    filename=f"creative_{idx+1}"
                )
            )
        return images
    except Exception as e:
        logger.error(
            "error loading generated images from file >> %s",
            e,
            exc_info=True
        )
