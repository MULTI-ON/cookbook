import datetime
import json
import os
import pickle
import time
from collections import defaultdict
from typing import List, Optional

import pytz
from dotenv import dotenv_values
from langchain.agents import Tool, tool
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.utilities.google_search import GoogleSearchAPIWrapper
from langchain.vectorstores import Chroma
from pydantic import BaseModel
from serpapi import GoogleSearch

if not os.getenv("RENDER"):
    env_config = dotenv_values(".local.env")
    OPENAI_MODEL_NAME = env_config.get("OPENAI_MODEL_NAME", "text-davinci-003")
    OPENAI_API_KEY = env_config.get("OPENAI_API_KEY", "")
    GOOGLE_API_KEY = env_config.get("GOOGLE_API_KEY", "")
    GOOGLE_CSE_ID = env_config.get("GOOGLE_CSE_ID", "")
    DATA_LOCATION = env_config.get("DATA_LOCATION", "")
else:
    OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME", "text-davinci-003")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")
    DATA_LOCATION = os.getenv("DATA_LOCATION")

NOTES_SCHEMA = {"idea": [], "reminder": [], "note": []}


def get_current_time_in_pt():
    # get the current time in UTC
    utc_now = datetime.datetime.now()
    # convert the current time to PT
    pt_now = utc_now.astimezone(pytz.timezone("US/Pacific"))
    return pt_now.strftime("%A, %b %d, %Y")


def notes_filename_for_user(phone_number: str) -> str:
    return f"{DATA_LOCATION}/notes_{phone_number}.pkl"


def load_notes_for_user(phone_number: str) -> List[str]:
    """Get the conversation history for a user."""
    # check if we have a memory file for this user
    notes_filename = notes_filename_for_user(phone_number)
    if os.path.exists(notes_filename):
        with open(notes_filename, "rb") as f:
            return pickle.load(f)
    else:
        return {}


def save_notes_for_user(phone_number: str, notes) -> None:
    """Save the conversation history for a user."""
    notes_filename = notes_filename_for_user(phone_number)
    with open(notes_filename, "wb") as f:
        pickle.dump(notes, f)


def get_chroma_client():
    embeddings = OpenAIEmbeddings(
        openai_api_key=OPENAI_API_KEY,
        document_model_name="text-embedding-ada-002",
        query_model_name="text-embedding-ada-002",
    )
    return Chroma(
        collection_name="notes",
        embedding_function=embeddings.embed_query,
        persist_directory=None,
    )


class Google(GoogleSearchAPIWrapper):
    def results(self, query, num_results, date_restrict=None):
        metadata_results = []
        results = self._google_search_results(
            query, num=num_results, dateRestrict=date_restrict
        )
        if len(results) == 0:
            return [{"Result": "No good Google Search Result was found"}]
        for result in results:
            metadata_result = {
                "title": result["title"],
                "link": result["link"],
            }
            if "snippet" in result:
                metadata_result["snippet"] = result["snippet"]
            metadata_results.append(metadata_result)

        return metadata_results


def internet_search(query, **kwargs):
    search_engine = Google(google_api_key=GOOGLE_API_KEY, google_cse_id=GOOGLE_CSE_ID)
    params = json.loads(query)
    q = params["query"]
    date_restrict = None if "date_restrict" not in params else params["date_restrict"]
    results = search_engine.results(q, 5, date_restrict)
    return results


class LocalResult(BaseModel):
    title: str
    description: Optional[str]

    def __repr__(self):
        if self.description:
            return self.title
        return f"{self.title}: {self.description}"


def google_maps_search(query, **kwargs):
    params = {
        "engine": "google_maps",
        "type": "search",
        "google_domain": "google.com",
        "q": query.strip(),
        "hl": "en",
        "api_key": os.environ["SERP_API_KEY"],
    }
    search = GoogleSearch(params)
    results = [LocalResult(**lr).dict() for lr in search.get_dict()["local_results"]]
    print(results)
    return results


def search_notes(query_json, **kwargs):
    """Takes argument in the form of a JSON Dictionary with query & filter parameters.
    {{
        "query": <str>, # This is used for semantic search so more description is helpful to find good results
        "filter": {{
            "before": <str> but in YYYY-MM-DD form (representing the end date of a date range),
            "after": <str> but in YYYY-MM-DD form (representing the start date of a date range)
        }}
    }}"""
    # Parse the LLM generated query
    chroma_client = get_chroma_client()
    query = json.loads(query_json)
    note_type = kwargs.get("type", "note")
    # Optionally filter emails based on the filter parameters
    # output = search_query_generator.run({"input": query["query"]})
    output = "foo"
    print("output")
    print(output)
    if output.lower().strip().strip('"').strip("'") == "none":
        keywords = []
    else:
        keywords = [
            t.strip().strip('"').strip("'").lower() for t in output.strip().split(" ")
        ]
    # generate date range filter in ints
    # generate keyword filter

    # Use semantic search to get top k results

    def datetime_to_int(dt):
        pass

    def create_dt_filter_param(before, after):
        return None

    metadata_filter = {}
    if "before" in query.get("filter", {}):
        metadata_filter["before"] = datetime_to_int(query["filter"]["before"])
    if "after" in query.get("filter", {}):
        metadata_filter["after"] = datetime_to_int(query["filter"]["after"])
    if note_type:
        metadata_filter["type"] = note_type
    if keywords:
        metadata_filter["keywords"] = keywords

    results = chroma_client.similarity_search(
        query["query"], k=20, filter=metadata_filter
    )

    if not results:
        return "No notes found matching the query"

    return results


def add_note(note, **kwargs):
    note_type = kwargs.get("type", "note")
    chroma_client = get_chroma_client()
    # get keywords w/ entity extraction
    seconds_past_epoch = int(time.time())
    doc = Document(page_content=note)
    metadata = {
        "datetime": seconds_past_epoch,
        "keywords": [],
        "type": note_type,
    }
    chroma_client.add_texts(texts=[doc], metadatas=[metadata])
    return f"I took a note of that -- stored as a {note_type}!"


def search_notes_dumb(query, **kwargs):
    user = kwargs.get("user", "")
    if not user:
        return "No user found"
    # load notes for user
    notes = load_notes_for_user(user)
    note_type = kwargs.get("type", "note")
    return notes.get(note_type, [])


def store_note_dumb(query, **kwargs):
    user = kwargs.get("user", "")
    if not user:
        return "No user found"
    note_type = kwargs.get("type", "note")
    notes = load_notes_for_user(user)
    if not note_type in notes:
        notes[note_type] = []
    full_note = f"{get_current_time_in_pt()}: {query}"
    notes[note_type].append(full_note)
    save_notes_for_user(user, notes)
    return "made a note!"


def human_clarification(query):
    return input()


def retrieve_ideas(query, **kwargs):
    return search_notes_dumb(query, type="idea", **kwargs)


def retrieve_reminders(query, **kwargs):
    return search_notes_dumb(query, type="reminder", **kwargs)


def store_reminder(query, **kwargs):
    return store_note_dumb(query, type="reminder", **kwargs)


def store_idea(query, **kwargs):
    return store_note_dumb(query, type="idea", **kwargs)

# Add multion toolkit

TOOLS = {
    # "ask_for_clarification": Tool(
    #     name="Ask for Clarification",
    #     func=human_clarification,
    #     description=f"Use this when you need to ask a clarifying question to the user (e.g. you do not know which tool to use, or need further info about how to categorize what the user just sent you.). The input to this is a question posed to the user asking for further clarification."
    # ),
    "take_note": Tool(
        name=f"Take Note",
        func=store_note_dumb,
        description="Use this for storing a note (a reminder, an idea, a fact that the user says is important, etc.).",
    ),
    # "internet_search": Tool(
    #     name="Internet Search",
    #     func=internet_search,
    #     description="""useful for when you need to answer questions about current events or people. You only have the ability to refine a search with this tool, you cannot click on links. Use only keywords in search, avoid boolean filters and other arguments.
    #     Use a json dictionary with the format below. The date_restrict parameter is optional, query is mandatory. Use the date_restrict parameter only if user is asking about something time-sensitive (e.g. recent news). General info (people / company) lookups should not use date_restrict.
    #     {{
    #         "query": <str> [the search query ].
    #         "date_restrict": <str> 'd[number]' or 'm[number]'. For example 'd7' for the past week or 'm1' for the past month.
    #     }}
    #     """,
    # ),
    "Google Maps Search": Tool(
        name="Google Maps Search",
        func=google_maps_search,
        description="""Use this for searching for restaurants on Google Maps. Examples:
- Vietnamese restaurant Hayes Valley
- French Restaurants Lower East Side""",
        return_direct=True,
    ),
    # "store_reminder": Tool(
    #     name=f"Create Reminder",
    #     func=store_reminder,
    #     description="Use this for storing a reminder."
    # ),
    # "store_idea": Tool(
    #     name=f"Store Idea",
    #     func=store_idea,
    #     description="Use this for storing an idea / brainstorm the user has shared."
    # ),
    # "retrieve_reminders": Tool(
    #     name=f"Retrieve Reminders",
    #     func=retrieve_reminders,
    #     description=f"Use this when the user is asking you what reminders they have."
    # ),
    "search_notes": Tool(
        name=f"Search Notes",
        func=search_notes_dumb,
        description=f"Use this when the user asks a question requiring looking something up from their notes, reminders, or ideas. If they ask what they're forgetting or what they should know about, you should use this.",
    ),
    # "retrieve_ideas": Tool(
    #     name=f"Retrieve Ideas",
    #     func=retrieve_ideas,
    #     description=f"Use this when a user is asking you about the ideas they've stored."
    # )
}


def get_tools():
    return list(TOOLS.values())
