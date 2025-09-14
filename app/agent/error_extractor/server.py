import uvicorn
from app.agent.agent_creator import create_agent
from google.adk.sessions import InMemorySessionService
from app.agent.error_extractor.agent import ErrorExtractorAgent, error_extractor_agent
import os

# Creating the agent card for the error executor agent
error_executor_agent_card = {
    "agent": {
        "name": "Image Error Extractor",
        "description": "Extracts all the key information from the image path given which caused the error and return a detailed analysis",
        "version": "1.0.0",
        "url": "http://localhost:8000",
    },
    "skills": {
        "name": "Extracting Error",
        "description": "Generates a detailed report from the image of what caused the error",
        "tags": ["error", "issue"],
    },
}
# Initalizing the agent session service
session_service = InMemorySessionService()
agent_runner = ErrorExtractorAgent(
    app_name=os.environ.get("APP_NAME"),
    session_service=session_service,
    agent=error_extractor_agent,
)
# Creating the agent server
app = create_agent(agent=agent_runner, agent_card=error_executor_agent_card)


# Starting the error extractor agent server
def start_error_extractor_agent():
    uvicorn.run(app, host="0.0.0.0", port=8000)
