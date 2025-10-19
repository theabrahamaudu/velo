# Velo AI

Velo AI is an agentic AI system that takes a user prompt for an ad campaign and returns a complete, ready-to-launch campaign: multi-platform text content, a recommended posting schedule, and thematic images.

The system is powered by a hierarchy of agents. At the top is the Supervisor Agent, which interprets the user’s prompt and delegates tasks to specialized agents:

* Audience Research Agent – analyzes the target audience and key interests.

* Content Generation Agent – creates ad copy, social posts, and emails.

* Scheduling Agent – builds an optimized posting schedule.

* Image Generation Agent – produces campaign visuals.

All agents have access to shared helper tools such as the URL Fetching Tool for retrieving relevant data.

The user interface is a Telegram bot with a simple, conversational chat experience; allowing users to create ad campaigns end-to-end without leaving the chat.

## System Architecture
Below is the project architecture. Each shaded area represents a separate module.

![image](https://github.com/theabrahamaudu/velo/blob/main/docs/Velo%20AI%20Architecture.png)

The modular architecture makes it easy to swap out components for other alternatives. Example swaps:  
* Swap out telegram polling for a web UI
* Swap out locally hosted LLM with SOTA cloud-based models
* Swap out bottlenacked local image generation model with SOTA image generation models

## Folder Structure


    velo-ai/
    ├── campaigns/
    ├── config/
    ├── db_data/
    ├── docs/
    ├── logs/
    ├── scripts/
    ├── tests/
    ├── velo/
    │   ├── agents/
    │   ├── db/
    │   ├── services/
    │   ├── telegram_interface/
    │   ├── types/
    │   ├── utils/
    │   ├── config.py
    │   ├── main.py
    │   └── server.py
    ├── velo.egg-info/
    ├── docker-compose.yml
    ├── Dockerfile
    ├── LICENSE
    ├── Makefile
    ├── MANIFEST.in
    ├── pyproject.toml
    ├── README.md
    └── requirements.txt

## Dependencies
#### OS Level
- Linux (Developed and tested on Ubuntu 22.04)
- Docker
- Ollama (Optionally on Docker too)

#### Python (3.11.11)
    # helper packages
    click==8.2.1
    Sphinx==8.2.3
    coverage==7.10.6
    flake8==7.3.0
    directory_tree==1.0.0

    # core packages
    python-dotenv==1.1.1
    pytest==8.4.1
    pytest_cov==6.2.1
    python-telegram-bot==22.3
    pyyaml==6.0.2
    pydantic==2.11.7
    sqlalchemy==2.0.43
    psycopg2-binary==2.9.10
    alembic==1.16.5


## Fun Fact
I tried to rawdog the whole thing; except for the Telegram interface (that part could easily be its own project). The idea is that with most LLM projects, people tend to reach for frameworks like LangChain to “make things easier,” but doing it with raw API calls and custom response parsers gives you finer control. You get to handle data exactly the way your app needs it, without the extra baggage or abstraction overhead of massive libraries. The goal here was to keep it lightweight, direct, and nimble.

## Installing
Spin up an instannce of Velo AI on your local machine by following these steps:
##### N.B: Originally developed with Python 3.11.xx, Ubuntu 22.04, Ollama and Docker

- Clone this repository
    ~~~
    git clone https://github.com/theabrahamaudu/velo.git
    ~~~
- Create a virtual environment
- Create a [Telegram bot](https://core.telegram.org/bots/features#botfather) and securely store the API Key you are given
- Install [Ollama](https://ollama.com/download/OllamaSetup.exe)
- Download the LLMs for offline inference generation:
    ~~~
    ollama pull mistral
    ollama pull llama3.1
    ~~~
- In a separate directory outside this project, setup Stable Diffusion with Automatic 1111:
    ~~~
    git clone https://github.com/AbdBarho/stable-diffusion-webui-docker.git .
    docker compose --profile download up --build
    docker compose --profile auto up --build
    ~~~
- Within the velo root diectory, create a `.env` file and add the following environment variables:
    ~~~
    # Telegram
    TG_TOKEN = your-telegram-token-BVHHGGH5667hjjd
    TIMEZONE = "Africa/Lagos"  # Change as necessary
    TIMEZONE_COMMON_NAME = "Lagos"  # Change as necessary

    # Database
    PUBLIC_HOST = http://localhost
    PORT = 8080
    DB_HOST = localhost
    DB_PORT = 5432
    DB_NAME = velo
    DB_USER = root
    DB_PASSWORD = your-db-password
    ~~~
- spin up Postres DB:
    ~~~
    docker compose up -d
    ~~~
- Optionally, edit system prompt in `./config/config.yml` to change the name of the agent
- Finally, start the message polling service to interact with Velo AI via Telegram:
    ~~~
    .venv/bin/python ./velo/main.py
    ~~~

    ### Quick Start (Post Install)

        cd velo-ai
        docker start stable-diffusion-auto-1
        docker start velo-postgres
        .venv/bin/python ./velo/main.py


## Help
Feel free to reach out to me or create a new issue if you encounter any problems setting up or running Velo AI.

## Possible Improvements/Ideas

- [ ] Unit tests
- [ ] Prompt engineering for system prompts
- [ ] Modify model client modules to use SOTA models
- [ ] Go crazy with Telegram Interface
- [ ] Build out web server and connect with custom web UI
- [ ] Integrate with social media platforms and post content directly from Velo interface
- [ ] Cloud deployment 

## Authors

Contributors names and contact info

*Abraham Audu*

* GitHub - [@the_abrahamaudu](https://github.com/theabrahamaudu)
* X (formerly Twitter) - [@the_abrahamaudu](https://x.com/the_abrahamaudu)
* LinkedIn - [@theabrahamaudu](https://www.linkedin.com/in/theabrahamaudu/)
* Instagram - [@the_abrahamaudu](https://www.instagram.com/the_abrahamaudu/)
* YouTube - [@DataCodePy](https://www.youtube.com/@DataCodePy)

## Version History

* See [commit change](https://github.com/theabrahamaudu/velo/commits/main/)
* See [release history](https://github.com/theabrahamaudu/velo/releases)

## Acknowledgments

* This [video series](https://www.youtube.com/watch?v=x-rCtwsz174&list=PLwHDUsnIdlMykhodmwoe9D6D9KYL0vRbl) by Alex The Dev inspired this project
* [ChatGPT](chat.openai.com) assisted with drafting the elaborate [Technical Requirement Document](https://github.com/theabrahamaudu/velo/blob/main/docs/VeloDocs.md) (implemented with necessary modifications during development).
