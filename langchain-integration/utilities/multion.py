"""Util that calls Multion Client.

In order to set this up, follow instructions at:
https://multion.notion.site/Download-MultiOn-ddddcfe719f94ab182107ca2612c07a5
"""
from typing import Dict, List,Any


import requests
from pydantic import BaseModel, Extra, root_validator

from langchain.utils import get_from_dict_or_env
import multion

class MultionAPI:
    def __init__(self):
        self.tabId = None
        self.new_session_count = 0

    def create_session(self, query: str, url: str) -> str:
        """Always the first step to run any activities that can be done using browser.
        The function parameters 'query' and 'url' both are compulsary.
        'query' is the query that you need to perform in the given url.if there is no 'query'set it as open.
        'url' is the base url of a site."""
        # Only create new session once and continue using update session
        if self.new_session_count < 2:
            response = multion.new_session({"input": query,"url": url})
            self.new_session_count +=1
            self.tabId = response['tabId']
            return  response['message']
        else:
            return "Continue using update session"

    def update_session(self, query:str,url:str) -> str:
        """Updates the existing browser session created using create_session with given action and url, used consequently to handle browser activitites after creating one session of browser.
        The function parameters 'query' and 'url' both are compulsary.
        'query' is the query that you need to perform in the given url.if there is no 'query'set it as open.
        'url' is the base url of a site."""
        response = multion.update_session(self.tabId, {"input": query,"url": url})
        return  response['message']



class MultionClientAPIWrapper(BaseModel):
    """Wrapper for Multion Client API.

    In order to set this up, follow instructions at:
    NEED TO ADD
    """

    multion_subscription_key: str
    client: Any = MultionAPI()

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = False

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""
        try:
            import multion
        except ImportError:
            raise ImportError(
                "Could not import multion python package. "
                "Please install it with `pip install multion`."
            )
        
        """Attention required"""
        client_id = get_from_dict_or_env(values, "client_id", "MULTION_CLIENT_ID")
        auth_password = get_from_dict_or_env(values, "auth_password", "MULTION_CLIENT_PASSWORD")
        values["from_number"] = get_from_dict_or_env(
            values, "from_number", "TWILIO_FROM_NUMBER"
        )
        values["client"] = Client(account_sid, auth_token)
        return values

    def run(self, task: str, url: str,tabId:Any) -> str:
        """Run body through Multion Client and respond with action.

        Args:
            task: 
            url: 
            tabId:
        """  
        if self.client.tabId == None or tabId==None :
            message = self.client.create_session(task,url)
        else:
            message = self.client.update_session(task,url)

        return message
