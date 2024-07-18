# Competitor Research

Use MultiOn Agents as part of an overarching competitor analysis workflow.

## How to run

Prerequisite: Ensure that you have `poetry` installed: [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation)

1. Install required packages with poetry:

```bash
poetry install
```

2. Set the OpenAI and MultiOn API Keys in `main.py`. Optionally, modify the task by changing the `business_description` field in `analyst.run()`

3. Run the Analyst Agent!

```bash
poetry run python main.py
```

## Explanation

The main coordinating agent is defined in the `Analyst` class in `agent.py`. The system prompt and tool options are defined in `prompts.py`.

The agent's loop is defined in `Analyst`'s `run` method. It passes the system prompt and user input (business description) to the agent and allows it to call MultiOn Agents as tools to accomplish the goal.

The overarching agent uses `GPT-4o` for its tool-calling capabilities.
