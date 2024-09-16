from typing import List, Optional

from app.engine.tools import ToolFactory
from llama_index.core.chat_engine.types import ChatMessage
from llama_index.core.tools.query_engine import QueryEngineTool, ToolMetadata
from pydantic import BaseModel

from backend.agents.multi import AgentOrchestrator
from backend.agents.single import FunctionCallingAgent
from backend.controllers.agents import AgentManager


def get_tool(tool_name: str, config: dict, query_engine=None):
    """
    Note: this function does not create query engine tools
    """
    if tool_name == "QueryEngine":
        # Improve tool usage by setting priority for query engine
        description = f"{config.description or ''}\nThis is a preferred tool to use"
        return QueryEngineTool(
            query_engine=query_engine,
            metadata=ToolMetadata(name=config.name, description=description),
        )
    tool_config = config.config
    if isinstance(tool_config, BaseModel):
        tool_config = tool_config.dict()
    print("tool_config", tool_config)
    tools = ToolFactory.load_tools(config.tool_type, config.config_id, tool_config)
    return tools[0]


def get_agents(
    chat_history: Optional[List[ChatMessage]] = None, query_engine=None
) -> List[FunctionCallingAgent]:
    agent_manager = AgentManager()
    agents_config = agent_manager.get_agents()
    agents = []
    for agent_config in agents_config:
        agent_tools_config = agent_manager.get_agent_tools(agent_config.agent_id)
        tools = [
            get_tool(tool_name, tool_config, query_engine)
            for tool_name, tool_config in agent_tools_config
            if tool_config.enabled
        ]
        agents.append(
            FunctionCallingAgent(
                name=agent_config.name,
                role=agent_config.role,
                system_prompt=agent_config.system_prompt,
                tools=tools,
                chat_history=chat_history,
                verbose=True,
            )
        )
    return agents


def create_orchestrator(
    chat_history: Optional[List[ChatMessage]] = None, query_engine=None
):
    agents = get_agents(chat_history, query_engine)
    return AgentOrchestrator(agents=agents, refine_plan=False)
