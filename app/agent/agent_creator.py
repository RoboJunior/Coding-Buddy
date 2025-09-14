from fastapi import FastAPI
from app.agent.error_extractor.agent import BaseAgent
from app.schema.agent_message import AgentMessage


# Create a agent server
def create_agent(agent: BaseAgent, agent_card: dict):
    agent_ = agent_card["agent"]
    agent_skills = agent_card["skills"]

    # Initalize the fastapi app
    app = FastAPI()

    # Run the agent executor
    @app.post("/run", tags=[agent_["name"]])
    async def run(message: AgentMessage):
        return await agent.execute(message=message)

    # Get the agent card
    @app.get("/.well-known/agent.json", tags=[agent_["name"]])
    async def agent_card():
        return {"agent": agent_, "skills": agent_skills}

    return app
