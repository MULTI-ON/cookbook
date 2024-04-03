import multion
import json
import pytest


class TestSession:
    def test_create_session(self):
        multion.set_api_url("http://localhost:8080/public/api/v1")
        multion.login(use_api=True, multion_api_key="bd2b652344b1496db2dbde807c7ffc83")

        # multion.set_remote(True)

        response = multion.create_session(
            {"url": "https://www.google.com", "includeScreenshot": True}
        )
        session_id = response["session_id"]
        step_session_payload = {
            "input": "whats the weather in australia",
            "url": "https://www.google.com",
        }
        step_session_response = multion.step_session(session_id, step_session_payload)
        print(step_session_response)

    def test_create_session_stream(self):
        multion.set_api_url("http://localhost:8080/public/api/v1")
        multion.login(use_api=True, multion_api_key="bd2b652344b1496db2dbde807c7ffc83")

        # multion.set_remote(True)

        response = multion.create_session(
            {"url": "https://www.google.com", "includeScreenshot": True}
        )
        session_id = response["session_id"]
        step_session_payload = {
            "input": "whats the weather in australia",
            "url": "https://www.google.com",
            "stream": True,
        }
        step_session_response = multion.step_session(session_id, step_session_payload)
        for chunk in step_session_response:
            if chunk:
                print(chunk)
