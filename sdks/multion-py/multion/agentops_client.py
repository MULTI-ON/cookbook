from agentops import Client, Event
from typing import List
import os

# remove
import pprint


class AgentOpsClient:
    def __init__(self, api_key: str = None, org_key: str = None):
        self._api_key = api_key or os.getenv("AGENTOPS_API_KEY")  # TODO
        self._org_key = org_key or os.getenv("AGENTOPS_ORG_KEY")
        self.current_event = Event(event_type="api")
        self.client = Client(api_key=self._api_key,
                             tags=['multion'],
                             org_key=self._org_key,
                             bypass_new_session=True)

    def start_session(self):
        self.client.start_session()

    def add_tags(self, tags: List[str]):
        self.client.add_tags(tags)

    def record(self, **kwargs):
        print("Recording event")
        # if self.client:
        self.current_event = Event(
            event_type=self.current_event.action_type, action_type=self.current_event.action_type, **kwargs)
        pprint.pprint(self.current_event)
        self.client.record(self.current_event)

    def end_session(self, end_state="Success"):
        if self.client:
            self.client.end_session(end_state=end_state)
