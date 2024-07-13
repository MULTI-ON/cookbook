import os
import instructor
from multion.client import MultiOn
from prefect import task, flow
from prefect.task_runners import ConcurrentTaskRunner
from openai import OpenAI
from type import Task, TaskList
from viz import visualize_task_list
from dotenv import load_dotenv
from worker import WorkerAgent

load_dotenv()


class ManagerAgent:
    def __init__(
        self,
        objective: str = "",
        model_name: str = "gpt-4o",
        use_openai=True,
    ):
        self.objective = objective
        self.model_name = model_name

        if use_openai:
            self.client = instructor.from_openai(
                OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            )
        else:
            raise NotImplementedError

    def generate_tasks(self, objective: str) -> TaskList:
        self.system_prompt = "You are an expert task manager that manages agents that each does one task. You decide how many agents is needed to do the meta-task, and what each agent's task is. The agents tasks should be done in parallel."

        self.user_prompt = f"""
                Create the tasks items for the following objective: {objective}
                """

        return self.client.chat.completions.create(
            model=self.model_name,
            response_model=TaskList,
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt,
                },
                {
                    "role": "user",
                    "content": self.user_prompt,
                },
            ],
        )

    @task
    def final_reduce(self, sessions: list) -> list:
        # Aggregate the results of the Multion sessions to get the top 10 frontend engineers.
        # For simplicity, we are returning the sessions as-is in this example.
        return sessions

    # Function to notify user (can be used to log the result or send a notification)
    @task
    def notify_user(self, action_results: list) -> None:
        for result in action_results:
            print(f"Notification to User: {result}")


@flow(name="Agent Flow", task_runner=ConcurrentTaskRunner())
def main(manager, objective: str):
    # Generate the tasks for the agents
    output_dict = manager.generate_tasks(objective)
    print(output_dict)

    tasks = output_dict.tasks
    # Uncomment to visualize tasks
    # visualize_task_list(tasks)

    cmds = [task.cmd for task in tasks]
    urls = [task.url for task in tasks]

    # Since we're running multiple tasks in parallel, we use Prefect's mapping to execute the same task with different inputs.
    # In this case, since the input is constant, we use 'unmapped' to prevent Prefect from trying to map over it.
    # Use map to execute perform_task for each cmd and url
    results = WorkerAgent.perform_task.map(cmds, urls)

    print("Results: ", results)
    # Reduce phase: process results as needed
    final_result = manager.final_reduce(manager, results)

    # Notify the user; this could also be sending an email, logging the result, etc.
    notification = manager.notify_user(manager, final_result)
    return notification
