# Job Search with MultiOn

Use MultiOn Agents as part of an overarching workflow where we find a job and apply to it.

## How to run

Prerequisite: Ensure that you have `poetry` installed: [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation)

1. Install required packages with poetry:

```bash
poetry install
```

2. Set the OpenAI and MultiOn API Keys in `main.py`. Optionally, modify the task by changing the `user_info` field in `agent.run()`

3. Run the Job Search Agent!

```bash
poetry run python main.py
```

## Explanation

The main coordinating agent is defined in the `Agent` class in `agent.py`. The system prompt and tool options are defined in `prompts.py`.

The agent's loop is defined in `Agent`'s `run` method. It passes the system prompt and user input (user self-description) to the agent and allows it to call MultiOn Agents as tools to accomplish the goal.

The overarching agent uses `GPT-4o` for its tool-calling capabilities.
