from agentops import Client, Event
from typing import List
import os


class AgentOpsClient:
    def __init__(self, api_key: str = None, org_key: str = None):
        self._api_key = api_key or os.getenv("AGENTOPS_API_KEY")
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

    def record(self):
        if self.client:
            self.client.record(self.current_event)

    def end_session(self):
        self.client.end_session(end_state="Success")
