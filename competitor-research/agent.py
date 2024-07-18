from multion.client import MultiOn
from prompts import orchestrator_prompt, orchestrator_state_prompt, orchestrator_tools
import json
from openai import OpenAI


class Analyst:
    def __init__(self, oai_key, multion_key):
        self.done = True
        self.state = ""
        self.oai_client = OpenAI(api_key=oai_key)
        self.multion_client = MultiOn(api_key=multion_key)

    # tool
    def browse(self, start_url, command):
        browse = None
        try:
            browse = self.multion_client.browse(
                cmd=command, url=start_url, max_steps=10
            )
        except Exception as e:
            print(e)
            browse = "Browsing session failed."
        return str(browse)

    # tool
    def retrieve(self, url, command):
        retrieve = None
        try:
            retrieve = self.multion_client.retrieve(
                url=url, cmd=command, scroll_to_bottom=True, render_js=True
            )
        except Exception as e:
            print(e)
            retrieve = "Retrieve failed."
        return str(retrieve)

    # tool
    def update_state(self, state):
        self.state = state

    def process_tool_call(self, tool_call):
        print(tool_call)
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        if function_name == "browse":
            start_url = function_args.get("start_url")
            command = function_args.get("command")
            browse_output = self.browse(start_url, command)
            self.messages.append(
                {
                    "role": "user",
                    "content": "Here is the browse output for start_url {start_url} and command {command}: {browse_output}".format(
                        start_url=start_url,
                        command=command,
                        browse_output=browse_output,
                    ),
                }
            )
        if function_name == "retrieve":
            url = function_args.get("url")
            command = function_args.get("command")
            retrieve_output = self.retrieve(url, command)
            self.messages.append(
                {
                    "role": "user",
                    "content": "Here is the retrieve output for url {url} and command {command}: {retrieve_output}".format(
                        url=url, command=command, retrieve_output=retrieve_output
                    ),
                }
            )
        if function_name == "update_state":
            state = function_args.get("state")
            self.update_state(state)
        if function_name == "done":
            self.done = True
        return None

    def prepare_messages(self):
        messages = self.messages + [
            {
                "role": "user",
                "content": orchestrator_state_prompt.format(state=self.state),
            }
        ]
        return messages

    def call(self):
        messages = self.prepare_messages()
        chat_completion = self.oai_client.chat.completions.create(
            messages=messages,
            model="gpt-4o",
            tools=orchestrator_tools,
            tool_choice="auto",
        )
        response_message = chat_completion.choices[0].message
        tool_calls = response_message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                self.process_tool_call(tool_call)

    def run(self, business_description):
        self.done = False
        self.messages = [
            {
                "role": "user",
                "content": orchestrator_prompt.format(
                    business_description=business_description
                ),
            }
        ]
        while not self.done:
            self.call()
        return self.state
