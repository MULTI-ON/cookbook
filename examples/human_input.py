"""Tool for asking human input."""

from typing import Callable, Optional, Type

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.pydantic_v1 import Field
from langchain.tools.base import BaseTool
from pydantic import BaseModel, Field

from typing import List, Union
from langchain.tools import tool
from langchain.tools import StructuredTool

# def web_prompt_func(prompt):
#     # Send the prompt to the web application
#     # This will depend on how your web application is set up
#     pass


# def web_input_func():
#     # Wait for the web application to send a response
#     # This could be done by setting up an endpoint that waits for a POST request
#     @app.route("/get_input", methods=["POST"])
#     def get_input():
#         user_input = request.form["user_input"]
#         return user_input


class Answer(BaseModel):
    answer: str


class Question(BaseModel):
    question: str = Field("Question to ask the human")


class HumanInput(BaseModel):
    questions: List[str] = Field("List of questions to ask the human")


def get_input() -> str:
    print("Insert your text. Enter 'q' or press Ctrl-D (or Ctrl-Z on Windows) to end.")
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "q":
            break
        contents.append(line)
    return "\n".join(contents)


def _print_func(questions: List[str]) -> None:
    print("\n")
    print("\n".join(questions))


class HumanInputRun(BaseTool):
    """Tool that asks user for input."""

    name: str = "human"
    description: str = (
        "Asks a human for inputs when you need to ask a user for info or not sure what to do next."
        "The input should be a list of questions for the human."
    )
    prompt_func: Callable[[str], None] = Field(default_factory=lambda: _print_func)
    input_func: Callable = Field(default_factory=lambda: input)
    args_schema: Type[BaseModel] = HumanInput

    def _run(
        self,
        questions: List[str],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the Human input tool."""
        self.prompt_func(questions)
        return self.input_func()
