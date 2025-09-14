from pydantic import BaseModel

class AgentMessage(BaseModel):
    query: str
    session_id: str
    user_id: str
