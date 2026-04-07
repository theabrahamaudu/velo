import requests
from ddgs import DDGS
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

    def url_caller(self, url: str, campaign_id: int) -> str:
        logger.info("loading web url >> %s", url)
        try:
            response = self.session.get(url)
            response = str(response.json())
        except Exception as e:
            response = str(e)
        return response

    def web_search_engine(self, query: str, campaign_id: int) -> str:
        logger.info("searching DuckDuckGo with query >> %s", query)
        try:
            response = DDGS().text(
                query=query,
                region="wt-wt",
                safesearch="off",
                timelimit="7d",
                max_results=5
            )
        except Exception as e:
            response = str(e)
        return str(response)
