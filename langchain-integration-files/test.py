from langchain.agents.agent_toolkits import create_multion_agent
from langchain.tools.multion.tool import MultionClientTool
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
agent_executor = create_multion_agent(
    llm=ChatOpenAI(temperature=0),
    tool=MultionClientTool(),
    agent_type=AgentType.OPENAI_FUNCTIONS
)

print(agent_executor.run(input="hi",task="show beutiful pictures of new york",url="www.google.com"))