import uvicorn
from app.agent.agent_creator import create_agent
from google.adk.sessions import InMemorySessionService
from app.agent.orchestrator.agent import OrchestratorAgent, orchestrator_agent
import os

# Creating the agent card for the error executor agent
orchestrator_agent_card = {
    "agent": {
        "name": "orchestrator_agent",
        "description": "Agent Orchestrator that breaks down user queries into subtasks, delegates them to suitable agents, ensures completion, integrates results, and extracts key error details with a one-line fix from GitHub, Stack Overflow, and Reddit.",
        "version": "1.0.0",
    },
    "skills": [
        {
            "name": "Get Agent Cards",
            "description": "Fetch metadata of all available agent cards and their skills.",
            "tags": ["agents", "metadata", "skills", "discovery"],
        },
        {
            "name": "Call Agent",
            "description": "Call an agent with a given query, session ID, and user ID to complete the task.",
            "tags": ["agents", "execution", "task", "orchestration"],
        },
    ],
}
# Initalizing the agent session service
session_service = InMemorySessionService()
agent_runner = OrchestratorAgent(
    app_name=os.environ.get("APP_NAME"),
    session_service=session_service,
    agent=orchestrator_agent,
)
# Creating the agent server
app = create_agent(agent=agent_runner, agent_card=orchestrator_agent_card)


# Starting the error extractor agent server
def start_orchestrator_agent():
    uvicorn.run(app, host="0.0.0.0", port=8002)
