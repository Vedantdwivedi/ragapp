from datetime import datetime
from typing import Dict, List, Tuple

import yaml

from backend.constants import AGENT_CONFIG_FILE
from backend.controllers.agent_prompt_manager import AgentPromptManager
from backend.models.agent import AgentConfig, ToolConfig
from backend.models.tools import (
    DuckDuckGoTool,
    E2BInterpreterTool,
    ImageGeneratorTool,
    OpenAPITool,
    QueryEngineTool,
    WikipediaTool,
)


class AgentManager:
    def __init__(self):
        self.available_tools = {
            "DuckDuckGo": DuckDuckGoTool,
            "Wikipedia": WikipediaTool,
            "OpenAPI": OpenAPITool,
            "Interpreter": E2BInterpreterTool,
            "ImageGenerator": ImageGeneratorTool,
            "QueryEngine": QueryEngineTool,
        }
        self.config = self.load_config_file()
        self._ensure_all_tools_exist()

    @staticmethod
    def load_config_file() -> Dict:
        try:
            with open(AGENT_CONFIG_FILE, "r") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Agent config file {AGENT_CONFIG_FILE} not found!")

    def _ensure_all_tools_exist(self):
        updated = False
        for agent_id, agent_data in self.config.items():
            if "tools" not in agent_data:
                agent_data["tools"] = {}

            # Add missing tools
            for tool_name in self.available_tools:
                if tool_name not in agent_data["tools"]:
                    agent_data["tools"][tool_name] = ToolConfig().dict()
                    updated = True

        if updated:
            self._update_config_file()

    def _update_config_file(self):
        with open(AGENT_CONFIG_FILE, "w") as file:
            yaml.dump(self.config, file)

    def get_agents(self) -> List[AgentConfig]:
        agents = [
            AgentConfig(agent_id=agent_id, **agent_data)
            for agent_id, agent_data in self.config.items()
        ]
        return sorted(agents, key=lambda x: x.created_at)  # Sort by creation time

    def create_agent(self, agent_data: Dict) -> AgentConfig:
        if "agent_id" not in agent_data:
            agent_data["agent_id"] = AgentConfig.create_agent_id(agent_data["name"])

        if "role" not in agent_data:
            raise ValueError("Role is required when creating an agent")

        agent_data["created_at"] = datetime.utcnow()

        if "tools" not in agent_data:
            agent_data["tools"] = {}
        for tool_name in self.available_tools:
            if tool_name not in agent_data["tools"]:
                agent_data["tools"][tool_name] = ToolConfig().dict()

        new_agent = AgentConfig(**agent_data)
        self.config[new_agent.agent_id] = new_agent.dict(exclude={"agent_id"})
        self._update_agent_config_system_prompt(new_agent.agent_id)
        self._update_config_file()
        return new_agent

    def update_agent(self, agent_id: str, data: Dict):
        if agent_id not in self.config:
            raise ValueError(f"Agent with id {agent_id} not found")

        updated_data = self.config[agent_id].copy()
        updated_data.update(data)
        updated_data["agent_id"] = agent_id

        if "role" not in updated_data:
            raise ValueError("Role is required when updating an agent")

        if "tools" not in updated_data:
            updated_data["tools"] = {}
        for tool_name in self.available_tools:
            if tool_name not in updated_data["tools"]:
                updated_data["tools"][tool_name] = ToolConfig().dict()

        updated_agent = AgentConfig(**updated_data)
        self.config[agent_id] = updated_agent.dict(exclude={"agent_id"})
        self._update_agent_config_system_prompt(agent_id)
        self._update_config_file()
        return updated_agent

    def delete_agent(self, agent_id: str):
        if agent_id in self.config:
            del self.config[agent_id]
            self._update_config_file()

    def get_agent_tools(self, agent_id: str) -> List[Tuple[str, object]]:
        agent = self.config.get(agent_id)
        if not agent:
            return []

        tools = []
        for tool_name, tool_config in agent.get("tools", {}).items():
            if tool_config["enabled"]:
                kwargs = {}
                kwargs["config"] = tool_config["config"]
                kwargs["enabled"] = tool_config["enabled"]
                tool = self._get_tool(tool_name, **kwargs)
                if tool:
                    tools.append((tool_name, tool))
        return tools

    def _get_tool(self, tool_name: str, **kwargs):
        tool_class = self.available_tools.get(tool_name)
        if tool_class:
            return tool_class(**kwargs)
        else:
            raise ValueError(f"Tool {tool_name} not found")

    def update_agent_tool(self, agent_id: str, tool_name: str, data: Dict):
        if agent_id not in self.config:
            raise ValueError(f"Agent {agent_id} not found")

        if "tools" not in self.config[agent_id]:
            self.config[agent_id]["tools"] = {}

        self.config[agent_id]["tools"][tool_name] = data
        # Update system prompts
        self._update_agent_config_system_prompt(agent_id)
        self._update_config_file()

    def _update_agent_config_system_prompt(self, agent_id: str):
        agent_config = self.config[agent_id]
        system_prompt = AgentPromptManager.generate_agent_system_prompt(agent_config)
        self.config[agent_id]["system_prompt"] = system_prompt

    def is_using_multi_agents_mode(self):
        return len(self.get_agents()) > 1

    def check_supported_multi_agents_model(self, model_provider: str, model: str):
        match model_provider:
            case "openai":
                from llama_index.llms.openai import OpenAI

                llm = OpenAI(model=model)
            case "anthropic":
                from llama_index.llms.anthropic import Anthropic

                llm = Anthropic(model=model)
            case "groq":
                from llama_index.llms.groq import Groq

                llm = Groq(model=model)
            case "ollama":
                from llama_index.llms.ollama import Ollama

                llm = Ollama(model=model)
            case "mistral":
                from llama_index.llms.mistralai import MistralAI

                llm = MistralAI(model=model)
            case _:
                return False

        return llm.metadata.is_function_calling_model

    @classmethod
    def is_model_supported_for_multi_agents(cls, model_provider: str, model: str):
        if (
            model_provider == "openai"
            or model_provider == "groq"
            or model_provider == "azure-openai"
            or model_provider == "ollama"
        ):
            return True
        elif model_provider == "mistral":
            from llama_index.llms.mistralai.utils import (
                is_mistralai_function_calling_model,
            )

            return is_mistralai_function_calling_model(model)
        return False


def agent_manager():
    return AgentManager()
