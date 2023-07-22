import json
import os
import pickle
from collections import defaultdict
from typing import List
from urllib.parse import parse_qs

from agents import setup_sync_agent
from dotenv import dotenv_values
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from sendblue import Sendblue
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

if not os.getenv("RENDER"):
    env_config = dotenv_values(".local.env")
    OPENAI_MODEL_NAME = env_config.get("OPENAI_MODEL_NAME", "text-davinci-003")
    OPENAI_API_KEY = env_config["OPENAI_API_KEY"]
    SENDBLUE_API_KEY = env_config["SENDBLUE_API_KEY"]
    SENDBLUE_API_SECRET = env_config["SENDBLUE_API_SECRET"]
    DATA_LOCATION = env_config["DATA_LOCATION"]
    TWILIO_PHONE_NUMBER = env_config["TWILIO_PHONE_NUMBER"]
    TWILIO_ACCOUNT_SID = env_config["TWILIO_ACCOUNT_SID"]
    TWILIO_AUTH_TOKEN = env_config["TWILIO_AUTH_TOKEN"]
else:
    OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME", "text-davinci-003")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SENDBLUE_API_KEY = os.getenv("SENDBLUE_API_KEY")
    SENDBLUE_API_SECRET = os.getenv("SENDBLUE_API_SECRET")
    DATA_LOCATION = os.getenv("DATA_LOCATION")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

app = FastAPI()
sendblue = Sendblue(SENDBLUE_API_KEY, SENDBLUE_API_SECRET)

# TODO db? pinecone?
AGENTS_IN_FLIGHT = {}

global AGENT_EXECUTING
AGENT_EXECUTING = defaultdict(bool)

# Map of user email to active user agent id
global ACTIVE_USER_AGENTS
ACTIVE_USER_AGENTS = defaultdict(str)


def memory_filename_for_user(phone_number: str) -> str:
    return f"{DATA_LOCATION}/memory_{phone_number}.pkl"


def load_memory_for_user(phone_number: str) -> List[str]:
    """Get the conversation history for a user."""
    # check if we have a memory file for this user
    memory_filename = memory_filename_for_user(phone_number)
    if os.path.exists(memory_filename):
        with open(memory_filename, "rb") as f:
            return pickle.load(f)
    else:
        return []


def load_memory_for_group(group_id: str) -> List[str]:
    """Get the conversation history for a user."""
    # check if we have a memory file for this user
    memory_filename = memory_filename_for_user(group_id)
    if os.path.exists(memory_filename):
        with open(memory_filename, "rb") as f:
            return pickle.load(f)
    else:
        return []


def save_memory_for_user(phone_number: str, memory: List[str]) -> None:
    """Save the conversation history for a user."""
    memory_filename = memory_filename_for_user(phone_number)
    with open(memory_filename, "wb") as f:
        pickle.dump(memory, f)


def save_memory_for_group(group_id: str, memory: List[str]) -> None:
    """Save the conversation history for a user."""
    memory_filename = memory_filename_for_user(group_id)
    with open(memory_filename, "wb") as f:
        pickle.dump(memory, f)


SENDBLUE_SCHEMA = {
    "accountEmail": "support@sendblue.co",
    "content": "Ahoy Developer!",
    "media_url": "some_cdn_link.png",
    "is_outbound": False,
    "status": "RECEIVED",
    "error_code": None,
    "error_message": None,
    "message_handle": "xxxxx",
    "date_sent": "2020-09-10T06:15:05.962Z",
    "date_updated": "2020-09-10T06:15:05.962Z",
    "from_number": "+19998887777",
    "number": "+19998887777",
    "to_number": "+15122164639",
    "was_downgraded": False,
    "plan": "blue",
}


class SendblueInput(BaseModel):
    accountEmail: str
    content: str = None
    media_url: str = None
    is_outbound: bool = False
    status: str = "RECEIVED"
    error_code: str = None
    error_message: str = None
    message_handle: str = None
    date_sent: str = None
    date_updated: str = None
    from_number: str = None
    number: str = None
    to_number: str = None
    was_downgraded: bool = False
    plan: str = "blue"


@app.post("/agent")
async def agent(request: Request):
    # todo also support pausing agent here
    print("received input!")
    body = await request.body()
    input_data_dump = body.decode()
    input_data = json.loads(input_data_dump)
    print("input_data")
    print(input_data)
    user = input_data.get("number")
    content = input_data.get("content")
    buffer = load_memory_for_user(user)
    # TODO: check if agent is already running for this user, use agent scratchpad if so
    agent_executor = setup_sync_agent(buffer=buffer, user=user)
    inputs = {"input": content}
    resp = agent_executor.run(inputs)
    response = sendblue.send_message(
        user,
        {
            "content": resp,
        },
    )
    new_buffer = agent_executor.memory.buffer
    save_memory_for_user(user, new_buffer)
    return {"resp": resp}


RULES_OF_ENGAGEMENT = """\
Hi everyone! I'm Mion and I'm here to help you schedule dinner. Please \
indicate where you'd like dinner, which cusisine you'd like, and whether \
there are any dietary restrictions. I may ask follow up questions as well ☺️.

When you're ready for me to jump in, please say @mion"""


@app.post("/restaurant-agent")
async def restaurant_agent(request: Request):
    # todo also support pausing agent here
    print("received input!")
    body = await request.body()
    input_data_dump = body.decode()
    input_data = json.loads(input_data_dump)

    user = input_data.get("number")
    content = input_data.get("content")
    group_id = input_data.get("group_id")

    conversational_memory = load_memory_for_group(group_id)

    # Diamon
    if len(conversational_memory) == 0:
        save_memory_for_group(group_id, [f"Mion: {RULES_OF_ENGAGEMENT}"])
        return {"resp": RULES_OF_ENGAGEMENT}

    save_memory_for_group(group_id, [*conversational_memory, f"{user}: {content}"])
    conversational_memory = load_memory_for_group(group_id)

    if "@mion" in content.lower():
        agent_executor = setup_sync_agent(buffer=None, user=user)
        inputs = {
            "input": content,
            "chat_history": conversational_memory,
        }
        resp = agent_executor.run(inputs)
        sendblue.send_group_message(
            group_id,
            {"content": resp},
        )
        save_memory_for_group(group_id, [*conversational_memory, f"Mion: {resp}"])
        return {"resp": resp}


@app.post("/twilio_webhook")
async def twilio_webhook(request: Request):
    body = await request.body()
    input_data = body.decode()
    input_data_parsed = parse_qs(input_data)
    content = input_data_parsed.get("Body", [])
    user = input_data_parsed.get("From", [])
    if not content or not user or not len(content) or not len(user):
        return {"status": "error"}
    content = content[0]
    user = user[0]
    print("content")
    print(content)
    print("user")
    print(user)
    buffer = load_memory_for_user(user)
    # TODO: check if agent is already running for this user, use agent scratchpad if so
    agent_executor = setup_sync_agent(buffer=buffer, user=user)
    inputs = {"input": content}
    output = agent_executor.run(inputs)
    print("output")
    print(output)
    # resp = output.get("output")
    # Generate TwiML response
    response = MessagingResponse()
    response.message(output)
    # Send response back to the same phone number
    new_buffer = agent_executor.memory.buffer
    save_memory_for_user(user, new_buffer)

    # return the TwiML response as the HTTP response
    return Response(content=str(response), media_type="application/xml")
