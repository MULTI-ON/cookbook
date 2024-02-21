from agentops import Client, Event
from typing import List
import os


class AgentOpsClient:
    def __init__(self):
        self._api_key = None
        self._org_key = None
        self._client = None
        self.current_event = Event(event_type="api")

    @property
    def api_key(self):
        return self._api_key if self._api_key else os.getenv("AGENTOPS_API_KEY")

    @api_key.setter
    def api_key(self, value):
        self._api_key = value
        if value:
            os.environ["AGENTOPS_API_KEY"] = value

    @property
    def org_key(self):
        return self._org_key

    @org_key.setter
    def org_key(self, value):
        self._org_key = value

    # TODO: Call the setter to create the client
    @property
    def client(self):
        # if not self._client:
        #     self.client = None
        return self._client

    @client.setter
    def client(self, tags: List[str] = ["multion"]):
        self._client = Client(api_key=self.api_key,
                              tags=tags,
                              org_key=self.org_key)

    def record(self):
        if self.client:
            self.client.record(self.current_event)

    def end_session(self):
        self.client.end_session(end_state="Success")
