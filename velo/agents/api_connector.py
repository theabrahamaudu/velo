import requests
from velo.utils.types import Function, Parameters, Property, Tool
from velo.utils.agent_logs import agent as logger


class WebConnector:
    def __init__(self):
        self.session = requests.Session()

    def weather_api(self, city: str) -> str:
        logger.info("making weather API call for city >> %s", city)
        response = self.session.get(
            url="https://wttr.in/"+city+"?format=j1"
        )
        response = response.json()
        temp = response["current_condition"][0]["FeelsLikeC"]
        return temp


GET_WEATHER = Tool(
    type="function",
    function=Function(
        name="weather_api",
        description="fetch the temperature of a city in degrees celsius",
        parameters=Parameters(
            type="object",
            properties={
                "city": Property(
                    type="string",
                    description="name of the city to check weather conditions"
                )
            },
            required=["city"]
        )
    )
)
