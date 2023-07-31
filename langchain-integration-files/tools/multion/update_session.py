import base64
from email.message import EmailMessage
from typing import List, Optional, Type,Any

from pydantic import BaseModel, Field
from enum import Enum
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools.multion.base import MultionBaseTool

import multion




class UpdateSessionSchema(BaseModel):
    """Input for UpdateSessionTool."""
    tabID:int = Field(
        ...,
        description="The tabID, received from one of the createSessions run before"
    )
    query: str = Field(
        ...,
        description="The query to run in multion agent.",
    )
    url: str = Field(
        "www.google.com",
        description="The Url to run the agent at.",
    )
    
    


class MultionUpdateSession(MultionBaseTool):
    """
   `MultionUpdateSession` is a function for AI bots to update existing browser sessions. It requires three parameters: `TabId` (mandatory), `query`, and `url`. The function performs the specified `query` action in the given `url`, defaulting to 'open' if `query` is not provided. It returns the updated `tabID` and the response, enabling reuse for future runs in a multion environment."""

    name: str = "create_gmail_draft"
    description: str = (
        "Use this tool to create a new Multion Session with provided fields"
    )
    args_schema: Type[UpdateSessionSchema] = UpdateSessionSchema
    tabID:Any = None

   
    def _run(
         self,
         tabID:str,
        query: str,
        url: Optional[str] = "www.google.com",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict:
        try:
            try:
                response = multion.update_session(tabID,{"input": query,"url": url})
                content =  {"tabID":tabID,"Response":response["message"]}
                self.tabID = tabID
                return content
            except:
                 if(self.tabID!=None):
                    response = multion.update_session(tabID,{"input": query,"url": url})
                    content =  {"tabID":self.tabID,"Response":response["message"]}
                    return content
                                     
                 else:
                    response = multion.new_session({"input": query,"url": url})
                    self.tabID= response['tabID']
                    return {"tabID":response['tabID'],"Response":response["message"]}
        except Exception as e:
            raise Exception(f"An error occurred: {e}")
