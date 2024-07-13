from pydantic import BaseModel, Field
from typing import List, Optional


class Task(BaseModel):
    """Correctly resolved sub-task from the given objective.

    cmd (str): The detailed and specific natural language instruction for web browsing
    url (str): The best URL to start the session based on user instruction"""

    id: int
    name: str
    description: str
    cmd: str
    url: str


class TaskList(BaseModel):
    """Correctly resolved set of tasks from the given objective"""

    tasks: List[Task]
