from dotenv import dotenv_values
import os
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# from agents import setup_sync_agent
import multion


env_config = dotenv_values(".local.env")
OPENAI_MODEL_NAME = env_config.get("OPENAI_MODEL_NAME", "text-davinci-003")
OPENAI_API_KEY = env_config["OPENAI_API_KEY"]
DATA_LOCATION = env_config["DATA_LOCATION"]
os.environ["SERP_API_KEY"] = env_config["SERP_API_KEY"]
os.environ["SERPAPI_API_KEY"] = env_config["SERP_API_KEY"]
os.environ["GOOGLE_API_KEY"] = env_config["SERP_API_KEY"]




import datetime
import calendar


# multion.login()



current_datetime = datetime.datetime.now()
prefix_template = f"""You are Mion a chatbot interactiing in a group conversation to help the humans book  a restaurant.
You are given the task to find out the date,time, location and number of people for restaurant booking. from the conversation or chat_history
Use the following facts
1) Today's date  is {current_datetime.strftime("%m/%d/%Y")} in format (DD-MM-YYYY) is a {calendar.day_name[current_datetime.weekday()]}, to find out the actual date and day of booking."""

prefix_template = f""" You are Mion a chatbot interactiing in a group conversation to help the humans book  a restaurant.
You are given the task to find out the date,time, location and number of people for restaurant booking. from the conversation or chat_history.
Today is Thursday, the 28th of September 2023. Please provide me with a date in the format 'DD th Month YYYY' based on the chat_history,
 whether it's in the form of 'next Friday,' 'Tomorrow,' or any other expression they choose to use."""
template = prefix_template + """
Note: 
1) The chat_history will have conversations in the form {{Name}}: {{Message}}
2) Always output date in the form {{DD th Month YYYY}}, remember to use  the facts given above to predict out the date.
3) Telll the restaurant name and count of people in numerical form, based on the chat_history.
Use continuos tense in the output.

{chat_history}
Human: {human_input}
Chatbot:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"], template=template
)
memory = ConversationBufferMemory(memory_key="chat_history")




USERNAME="Div"
USER_EMAIL="div@multion.ai"


agent_chain = None

def add_only_input(query_input):
    global memory
    memory.save_context({"input": query_input},{"output":""})

def create_agent():
    llm = OpenAI(temperature=0)
    llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    memory=memory,
)
    return llm_chain

def talk_to_human(llm_chain,query_input):
    result = llm_chain.predict(human_input=query_input)
    if("Confirmed" not in result):
        result+="\n Enter 'CONFIRM' if the shown date, time and count of people is correct else tell the correct value"
    return result

def use_multion(prompt):
    multion.login()
    prompt = f"'{prompt}'Book a table with the details from above statement. Choose SanFracisco Location"
    multion.new_session({"input":prompt,"url":"https://www.opentable.com/all-metros"})
    