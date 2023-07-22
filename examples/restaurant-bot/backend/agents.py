import os
import uuid
from typing import Any, Dict, List, Tuple, Union, Optional

from dotenv import dotenv_values
from langchain import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentExecutor, ConversationalAgent, Tool
from langchain.agents import AgentType
from langchain.agents.tools import BaseTool, InvalidTool
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.schema import AgentAction, AgentFinish
from prompts import FORMAT_INSTRUCTIONS, PREFIX, SUFFIX
from tools import get_tools

if not os.getenv("RENDER"):
    env_config = dotenv_values(".local.env")
    OPENAI_MODEL_NAME = env_config.get("OPENAI_MODEL_NAME", "gpt-4")
    OPENAI_API_KEY = env_config.get("OPENAI_API_KEY", "")
else:
    OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME", "gpt-4")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class UserAgent(ConversationalAgent):

    user: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def from_llm_and_tools(cls, *args, **kwargs):
        agent = super().from_llm_and_tools(*args, **kwargs)
        agent.user = kwargs.get("user", "")
        return agent

    def tool_run_logging_kwargs(self) -> Dict:
        # tool_kwargs = super().tool_run_logging_kwargs()
        tool_kwargs = {}
        tool_kwargs["user"] = self.user
        return tool_kwargs
    
def setup_sync_agent(buffer=None, **kwargs):
    if buffer is None:
        buffer = []
    tools = get_tools()
    if kwargs.get("openai_api_key"):
        openai_api_key = kwargs.get("openai_api_key")
    else:
        openai_api_key = OPENAI_API_KEY
    llm = ChatOpenAI(
        temperature=0,
        openai_api_key=openai_api_key,
        max_tokens=1000,
        model_name=OPENAI_MODEL_NAME,
    )
    agent = UserAgent.from_llm_and_tools(
        llm=llm,
        tools=tools,
        prefix=PREFIX,
        suffix=SUFFIX,
        format_instructions=FORMAT_INSTRUCTIONS,
        ai_prefix="Mion",
    )
    print("buffer is ", buffer)
    # memory = ConversationBufferWindowMemory(
    #     buffer=buffer,
    #     input_key="input",
    #     output_key="output",
    #     memory_key="chat_history",
    #     k=3
    # )
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        # memory=memory,
        # pausing_tool_name="Ask for Clarification",
        **kwargs,
    )
    return agent_executor
