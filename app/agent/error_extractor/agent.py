from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, SseConnectionParams
from google.adk.agents.llm_agent import LlmAgent
from google.genai import types
from google.adk.runners import Runner
from dotenv import load_dotenv
from app.schema.agent_message import AgentMessage
from app.agent.base_agent import BaseAgent
from opik.integrations.adk import OpikTracer
import os

load_dotenv()

# Initalizing all the agent tools here
toolset = McpToolset(
    connection_params=SseConnectionParams(url=os.environ.get("MCP_SERVER_URL")),
    tool_filter=["error_tracer"],
)

# Initalizing the agent Observability
error_agent_tracer = OpikTracer(
    name="error_extractor",
    tags=["error", "issue"],
    metadata={
        "environment": "development",
        "model": os.environ.get("MODEL_NAME"),
        "framework": "google-adk",
        "example": "basic",
    },
    project_name="Coding-Buddy",
)


# ErrorExtractor Agent Class
class ErrorExtractorAgent(BaseAgent):
    # Intialize the agent variables
    def __init__(self, app_name, session_service, agent):
        super().__init__(app_name, session_service, agent)

    # Get the current session
    async def get_current_session(self, user_id: str, session_id: str):
        current_session = await self.session_service.get_session(
            app_name=self.app_name, user_id=user_id, session_id=session_id
        )
        if not current_session:
            current_session = await self.session_service.create_session(
                app_name=self.app_name, user_id=user_id, session_id=session_id
            )
        runner = Runner(
            agent=self.agent,
            app_name=self.app_name,
            session_service=self.session_service,
        )
        return runner

    # Agent Interaction
    async def execute(self, message: AgentMessage):
        runner = await self.get_current_session(
            session_id=message.session_id, user_id=message.user_id
        )
        content = types.Content(role="user", parts=[types.Part(text=message.query)])
        events = runner.run_async(
            user_id=message.user_id, session_id=message.session_id, new_message=content
        )

        agent_response = {}
        async for event in events:
            if event.get_function_calls():
                agent_response["function_calls"] = event.get_function_calls()
            elif event.get_function_responses():
                agent_response["function_responses"] = event.get_function_responses()
            elif event.is_final_response():
                agent_response["final_response"] = event.content.parts[0].text

        return agent_response


# Initalizing the error extractor agent
error_extractor_agent = LlmAgent(
    model=os.environ.get("MODEL_NAME"),
    name="error_extractor_agent",
    instruction="""
    Your a CodingBuddyErrorExtractor who is specialized in tracing the error how its caused.
    your task is to process the image and extract all the sufficient information about the caused error.
    return all the extracted information from the image.
    """,
    tools=[toolset],
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    before_agent_callback=error_agent_tracer.before_agent_callback,
    after_agent_callback=error_agent_tracer.after_agent_callback,
    before_model_callback=error_agent_tracer.before_model_callback,
    after_model_callback=error_agent_tracer.after_model_callback,
    before_tool_callback=error_agent_tracer.before_tool_callback,
    after_tool_callback=error_agent_tracer.after_tool_callback,
)
