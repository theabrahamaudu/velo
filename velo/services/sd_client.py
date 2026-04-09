import requests
from requests import Response
from velo.config import (
    SD_URL,
    OLLAMA_URL,
    XAI_MODEL_NAME,
    XAI_URL,
    XAI_API_KEY,
    MAX_RETRIES,
    LOCAL_INFERENCE
)
from velo.utils.service_logs import service as logger
from velo.types.agent import SDMessage


class ImageGenClient:
    def __init__(self, model: str) -> None:
        self.local: bool = LOCAL_INFERENCE
        if self.local:
            self.imgGen_url = SD_URL
            self.model = str(model)
        else:
            self.imgGen_url = XAI_URL
            self.model = XAI_MODEL_NAME
        self.session = requests.Session()

    def send(self, message: SDMessage) -> dict | None:
        logger.info("running query with %s model", self.model)
        count = 0
        try:
            max_retries = MAX_RETRIES
            for attempt in range(1, max_retries+1):
                count += 1
                if self.local:
                    self.flush_memory()
                    self.reload_server()
                response = self.make_request(message)
                if response.status_code == 200:
                    logger.info(
                        "byte64 imgages received as response >> %s ",
                        response.status_code,
                    )
                    return response.json()
                else:
                    logger.warning(
                        "attempt %s/%s: error generating response >> %s >> %s",
                        attempt,
                        max_retries,
                        response.status_code,
                        response.json()
                    )
        except Exception as e:
            logger.error(
                "image generation failed: err >> %s << after %s attempts",
                e,
                count
            )

    def flush_memory(self) -> None:
        try:
            response = self.session.get(url=OLLAMA_URL+"/api/ps")
            models: list = response.json()["models"]

            if len(models) > 0:
                for model in models:
                    resp = self.session.post(
                        url=OLLAMA_URL+"/api/chat",
                        json={
                            "model": model["name"],
                            "keep_alive": 0
                        },
                        headers={"Content-Type": "application/json"}
                    )
                assert resp.status_code == 200
                logger.info(
                    "flushed %s ollama models from GPU >> %s",
                    len(models),
                    [model["name"] for model in models]
                )
        except Exception as e:
            logger.error(
                "error flushing GPU memory %s",
                e,
                exc_info=True
            )

    def reload_server(self):
        try:
            response = self.session.get(
                url=self.imgGen_url+"/sdapi/v1/reload-ui"
            )
            logger.warning(
                "restarted SD server >> %s",
                response.json()
            )
        except Exception as e:
            logger.error(
                "error restarting SD server >> %s",
                e,
                exc_info=True
            )

    def _get_headers(self) -> dict:
        return {
                "Content-Type": "application/json"
            } if self.local else {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {XAI_API_KEY}"
            }

    def make_request(self, message: SDMessage) -> Response:
        if self.local:
            response = self.session.post(
                        url=self.imgGen_url+"/sdapi/v1/txt2img",
                        json={
                            "prompt": message.prompt,
                            "negative_prompt": message.negative_prompt,

                            "sampler_name": "DPM++ 2M",
                            "steps": 30,
                            "cfg_scale": 7,
                            "width": message.width,
                            "height": message.height,
                            "seed": -1,
                            "n_iter": 2,

                            "enable_hr": True,
                            "hr_scale": 2,
                            "hr_upscaler": "Latent (antialiased)",
                            "hr_second_pass_steps": 12,
                            "denoising_strength": 0.7,

                            "restore_faces": False
                        },
                        headers=self._get_headers()
                    )
        else:
            response = self.session.post(
                        url=self.imgGen_url,
                        json={
                            "prompt": message.prompt,
                            "model": self.model,
                            "n": 2,
                            "aspect_ratio": "16:9",
                            "response_format": "b64_json"
                        },
                        headers=self._get_headers()
                    )
        return response
