import base64
from email.message import EmailMessage
from typing import List, Optional, Type

from pydantic import BaseModel, Field
from enum import Enum
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools.multion.base import MultionBaseTool

import multion




class CreateSessionSchema(BaseModel):
    """Input for CreateSessionTool."""

    query: str = Field(
        ...,
        description="The query to run in multion agent.",
    )
    url: str = Field(
        "www.google.com",
        description="The Url to run the agent at.",
    )
    


class MultionCreateSession(MultionBaseTool):
    """Always the first step to run any activities that can be done using browser.The function parameters 'query' and 'url' both are compulsary. 'query' is the query that you need to perform in the given url.if there is no 'query'set it as open.'url' is the base url of a site. This returns the tabID and Response of the run, the tabID can be reused for UpdateSession."""

    name: str = "create_multion_session"
    description: str = (
        "Use this tool to create a new Multion Session with provided fields"
    )
    args_schema: Type[CreateSessionSchema] = CreateSessionSchema

   
    def _run(
         self,
        query: str,
        url: Optional[str] = "www.google.com",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict:
        try:
            response = multion.new_session({"input": query,"url": url})
            return {"tabID":response['tabID'],"Response":response["message"]}
        except Exception as e:
            raise Exception(f"An error occurred: {e}")
