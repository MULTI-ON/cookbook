"""Tool for Multion Extension API"""
import sys
from io import StringIO
from typing import Dict, Optional,Any

from pydantic import BaseModel, Field
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from langchain.utilities.multion import MultionClientAPIWrapper

class MultionClientTool(BaseModel):
    """Simulates a Browser interacting agent."""
    name = "Multion AI Extension Results in automated browser actions"
    description = (
        "A api to communicate with browser extension multion "
        "Useful for automating tasks and actions in the browser "
        "Input should be a task and a url."
        "The result is text form of action that was executed in the given url."
    )
    api_wrapper: MultionClientAPIWrapper

    def _run(
        self,
        task: str,
        url: str = "www.google.com",
        tabId: Optional[Any] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        return self.api_wrapper.run(task,url,tabId)

    async def _arun(
        self,
        task: str,
        url: str = "www.google.com",
        tabId: Optional[Any] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Multion Client does not support async yet")
