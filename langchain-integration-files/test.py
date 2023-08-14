# IMPORTS
from langchain.agents.agent_toolkits import MultionToolkit
import os
import multion
from langchain import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.agents.agent_toolkits import MultionToolkit

os.environ["LANGCHAIN_TRACING"] = "true"

# MultiOn Toolkit (pip install multion)
toolkit = MultionToolkit()
tools = toolkit.get_tools()
multion.login()  # MultiOn -> Login to the MultiOn Website

# Selecting LLM
key = "YOUR_OPENAI_API_KEY"
llm = OpenAI(temperature=0, openai_api_key=key)

# Intialize Agent
agent = initialize_agent(
    tools=toolkit.get_tools(),
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

# Running the Command
temp = agent.run("Show Beautiful Pictures of New York")
