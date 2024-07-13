from multion.client import MultiOn
from prefect import task
from dotenv import load_dotenv
import os

load_dotenv()


class WorkerAgent:
    @task
    @staticmethod
    def perform_task(input: str, url: str):
        client = MultiOn(api_key=os.getenv("MULTION_API_KEY"))
        session_id = WorkerAgent._start_session(client, url)

        should_continue = True
        try:
            while should_continue:
                updated_session = WorkerAgent._step_session(client, session_id, input)
                should_continue = updated_session.status != "DONE"
        except Exception as e:
            print(f"ERROR: {e}")

        WorkerAgent._close_session(client, session_id)

    @staticmethod
    def _start_session(client: MultiOn, url: str):
        response = client.sessions.create(url=url, local=True)
        print("New session started:", response.session_id)
        return response.session_id

    @staticmethod
    def _step_session(client: MultiOn, session_id: str, input_command: str):
        response = client.sessions.step(session_id, cmd=input_command)
        print("Session updated:", response.message)
        return response

    @staticmethod
    def _close_session(client: MultiOn, session_id: str):
        response = client.sessions.close(session_id)
        print("Session closed:", response.session_id)
