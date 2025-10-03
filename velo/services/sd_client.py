import requests
from requests import Response
from velo.config import SD_URL, OLLAMA_URL
from velo.utils.service_logs import service as logger
from velo.utils.types import SDMessage


class SDClient:
    def __init__(self, model: str) -> None:
        self.sd_url = SD_URL
        self.model = str(model)
        self.session = requests.Session()

    def send(self, message: SDMessage) -> dict | None:
        logger.info("running query with %s model", self.model)

        max_retries = 3
        for attempt in range(1, max_retries+1):
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
        logger.error(
            "image generation failed after %s attempts",
            max_retries
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
                url=self.sd_url+"/sdapi/v1/reload-ui"
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

    def make_request(self, message: SDMessage) -> Response:
        response = self.session.post(
                    url=self.sd_url+"/sdapi/v1/txt2img",
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
                    headers={"Content-Type": "application/json"}
                )
        return response
