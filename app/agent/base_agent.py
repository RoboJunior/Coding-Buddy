from abc import ABC, abstractmethod
from google.adk.sessions import InMemorySessionService
from google.adk.agents.llm_agent import LlmAgent
from app.schema.agent_message import AgentMessage


# BaseAgent Class to create all agents
class BaseAgent(ABC):
    def __init__(
        self, app_name: str, session_service: InMemorySessionService, agent: LlmAgent
    ):
        self.app_name = app_name
        self.session_service = session_service
        self.agent = agent

    @abstractmethod
    async def get_current_session(self, user_id: str, session_id: str):
        pass

    @abstractmethod
    async def execute(self, message: AgentMessage):
        pass
