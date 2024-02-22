from agentops import Client, Event
from typing import List
import os


class AgentOpsClient:
    def __init__(self, api_key: str = None, org_key: str = None, tags: List[str] = ["prod"]):
        self.current_event = Event(event_type="api")
        self.client = Client(api_key=api_key,
                             tags=tags,
                             org_key=org_key,
                             bypass_new_session=True)

    def start_session(self):
        if self.client:
            self.client.start_session()

    def record(self, **kwargs):
        if self.client:
            self.current_event = Event(
                event_type=self.current_event.event_type, action_type=self.current_event.action_type, **kwargs)
            self.client.record(self.current_event)

    def set_session_video(self, session_id: str):
        if self.client:
            self.agentops.client.session.set_session_video(
                f"{self.api_url}/sessionVideo/{session_id}")

    def end_session(self, end_state="Success"):
        if self.client:
            self.client.end_session(end_state=end_state)


__all__ = ['AgentOpsClient', 'Event']
