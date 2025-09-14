import uvicorn
from app.agent.agent_creator import create_agent
from google.adk.sessions import InMemorySessionService
from app.agent.stackredhub.agent import StackRedHub, stackredhub_agent
import os

# Creating the agent card for the error executor agent
stackredhub_agent_card = {
    "agent": {
        "name": "stackredhub",
        "description": "Extracts all key information that caused the error, returns a detailed analysis of the issue, and provides a clear one-line fix sourced from GitHub, Stack Overflow, and Reddit.",
        "version": "1.0.0",
        "url": "http://localhost:8001",
    },
    "skills": [
        {
            "name": "Extracting Error",
            "description": "Generates a detailed report of what caused the error",
            "tags": ["error", "issue"],
        },
        {
            "name": "Advanced Search",
            "description": "Rich search using filters like score, accepted answers, and comments.",
            "tags": ["search", "filters", "stackoverflow"],
        },
        {
            "name": "Analyze Stack Trace",
            "description": "Analyze a stack trace to search relevant questions on Stack Overflow.",
            "tags": ["stack trace", "stackoverflow", "analysis"],
        },
        {
            "name": "Search by Error (StackOverflow)",
            "description": "Search Stack Overflow by error message with all filters applied.",
            "tags": ["stackoverflow", "error message", "search"],
        },
        {
            "name": "Reddit Related Issues",
            "description": "Fetch similar issues from Reddit that were solved previously.",
            "tags": ["reddit", "issues", "solutions"],
        },
        {
            "name": "GitHub Related Issues",
            "description": "Fetch similar issues from GitHub that were solved previously.",
            "tags": ["github", "issues", "solutions"],
        },
    ],
}
# Initalizing the agent session service
session_service = InMemorySessionService()
agent_runner = StackRedHub(
    app_name=os.environ.get("APP_NAME"),
    session_service=session_service,
    agent=stackredhub_agent,
)
# Creating the agent server
app = create_agent(agent=agent_runner, agent_card=stackredhub_agent_card)


# Starting the error extractor agent server
def start_stackredhub_agent():
    uvicorn.run(app, host="0.0.0.0", port=8001)
