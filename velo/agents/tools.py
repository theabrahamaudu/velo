from logging import Logger
from velo.utils.types import (
    Function,
    Parameters,
    Property,
    Tool,
    ToolCall,
    Message
)

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

URL_CALLER = Tool(
    type="function",
    function=Function(
        name="url_caller",
        description="use python request module to make a get \
            request using the url provided and return a string \
            of the JSON response",
        parameters=Parameters(
            type="object",
            properties={
                "url": Property(
                    type="string",
                    description="url or link to be fetched from the internet"
                )
            },
            required=["url"]
        )
    )
)

AUDIENCE_TOOL = Tool(
    type="function",
    function=Function(
        name="audience_agent",
        description="carries out auduence research to create audience profile \
            with an output containing lists of keywords, interests and pain \
            points to inform content generation",
        parameters=Parameters(
            type="object",
            properties={
                "prompt": Property(
                    type="string",
                    description="prompt to the audience research agent \
                        describing the context of the ad campaign being \
                        worked on"
                )
            },
            required=["prompt"]
        )
    )
)


def get_result(
        tool_callables: dict,
        call: ToolCall,
        history: list[Message],
        logger: Logger):

    logger.info(
        "calling tool >> %s with args >> %s",
        call.function.name,
        call.function.arguments
    )
    result = tool_callables[call.function.name](**call.function.arguments)

    logger.info(
        "result from tool %s >> %s",
        call.function.name,
        result
    )

    history.append(
        Message(
            role="tool",
            content=result,
            tool_name=call.function.name
        )
    )

    return history
