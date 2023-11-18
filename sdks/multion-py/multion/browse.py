"""Multion tool spec."""

import base64
from io import BytesIO
from typing import Optional
import multion
import pytesseract
from PIL import Image


class MultionToolSpec:
    """MultiOn tool spec."""

    spec_functions = ["browse"]

    def __init__(
        self,
        token_file: Optional[str] = "multion_token.txt",
        default_url: Optional[str] = "https://google.com",
        mode: Optional[str] = "auto",
        use_api: Optional[bool] = False,
    ) -> None:
        """Initialize with parameters."""
        multion.login(use_api=use_api)

        self.current_status = "NOT_ACTIVE"
        self.session_id = None
        self.current_url = default_url
        self.mode = mode

    def browse(self, instruction: str, url: str):
        """
        Browse the web using MultiOn
        MultiOn gives the ability for LLMs to control web browsers using natural language instructions
        Always include an URL to start browsing from (default to https://www.google.com/search?q=<search_query> if no better option, where <search_query> is a generated query to Google.)

        You may have to repeat the instruction through multiple steps or update your instruction to get to
        the final desired state. If the status is 'CONTINUE', then reissue the same instruction to continue execution

        args:
            instruction (str): The detailed and specific natural language instruction for web browsing
            url (str): The best URL to start the session based on user instruction
        """
        # multion.set_remote(False)

        # If a session exists, update it. Otherwise, create a new session.
        if self.session_id:
            session = multion.update_session(
                self.session_id, {"input": instruction, "url": self.current_url}
            )

        else:
            session = multion.new_session(
                {"input": instruction, "url": url if url else self.current_url}
            )
            self.session_id = session["session_id"]

        # Update the current status and URL based on the session
        self._update_status(session)

        while self.mode == "auto" and (self.current_status == "CONTINUE"):
            session = multion.update_session(
                self.session_id, {"input": instruction, "url": self.current_url}
            )
            self._update_status(session)
            print(self.current_status, self.current_url)

        # Until agent completes the task we keep triggering agent
        # while (agent.current_status != 'DONE') {
        #     console.log("CURRENT STATUS:", agent.current_status);
        #     switch (agent.current_status) {
        #         case 'NOT_ACTIVE':
        #             response = await triggerAgent(userQuery, domain, agent);
        #             continue;
        #         case 'CONTINUE':
        #             domain = agent.current_url;
        #             response = await triggerAgent(userQuery, domain, agent);
        #             continue;
        #         case 'NOT SURE':
        #             let model_query = `YOU HAD ASKED USER THIS QUESTION PREVIOUSLY: ${agent.question}\n`;
        #             let user_response = `AND THIS IS THE USER'S RESPONSE TO THE QUESTION: ${agent.user_response}`;
        #             let new_query = userQuery + `\n` + model_query + user_response;
        #             console.log("New user query:", new_query)
        #             domain = agent.current_url;
        #             response = await triggerAgent(new_query, domain, agent);
        #             continue;
        #         case 'WRONG':
        #     }
        return {
            "status": session["status"],
            "url": session["url"],
            "action_completed": session["message"],
            "content": self._read_screenshot(session["screenshot"]),
        }

    def _update_status(self, session):
        """Update the current status and URL based on the session."""
        self.current_status = session["status"]
        self.current_url = session["url"]

    def _read_screenshot(self, screenshot) -> str:
        image_bytes = screenshot.replace("data:image/png;base64,", "")
        image = Image.open(self._bytes_to_image(image_bytes))

        return pytesseract.image_to_string(image)

    def _bytes_to_image(self, img_bytes):
        return BytesIO(base64.b64decode(img_bytes))
