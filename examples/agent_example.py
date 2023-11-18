import base64
import os
from io import BytesIO
from typing import Optional

from langchain.llms import OpenAI

from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI

os.environ["LANGCHAIN_TRACING"] = "true"
# os.environ['OPENAI_API_KEY'] = "<openai_api_key>"
from langchain.tools import StructuredTool
from human_input import HumanInputRun


import multion
from multion import MultionToolSpec


def agent(query: str):
    multion_toolkit = MultionToolSpec(use_api=True, mode="auto")
    # multion.set_remote(True)

    tool = StructuredTool.from_function(multion_toolkit.browse)
    human_input = HumanInputRun()

    llm = OpenAI(temperature=0)

    # Structured tools are compatible with the STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION agent type.
    agent_executor = initialize_agent(
        [tool, human_input],
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )

    return agent_executor.run(query)


PROMPT = f"""
You are an expert AI Agent whose job is to find and get a gpu on a given service HYPERSTACK (https://www.hyperstack.cloud). Pass in the full detailed instructions exactly as below to MultiOn for browsing.
    
    Here are the high-level steps:
    1. Login and go to reach the gpu selection page
    2. Click on the Load Provising profile and then select the multion-profile and load it
    3. After the profile has been correctly selected and loaded continue
    4. If an on-demand A100 GPU is available with 80GB RAM, then reserve it
    5. If reservation is successful, then enable ssh access and return public ip to access the machine
"""

agent(query=PROMPT)
