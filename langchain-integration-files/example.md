from langchain import OpenAI
from langchain.agents import initialize_agent, AgentType
llm = OpenAI(temperature=0)
from langchain.agents.agent_toolkits import MultionToolkit
toolkit = MultionToolkit()
tools=toolkit.get_tools()
agent = initialize_agent(
    tools=toolkit.get_tools(),
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
)

agent.run("show me best restaurants in New York.")