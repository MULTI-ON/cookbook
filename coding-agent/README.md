# Coding Agent

Spin up MultiOn agents to carry out Coding projects end-to-end!

## How to run

Prerequisite: Ensure that you have `poetry` installed: [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation)

1. Make sure that the MultiOn Chrome Extension is installed and enabled (for more details, see [here](https://docs.multion.ai/learn/browser-extension)).

2. Install required packages with poetry:

```bash
poetry install
```

3. Run the coding agent! Make sure that you are logged into Replit.

```bash
poetry run gradio app.py
```

## Explanation

This is essentially a sample attempt at trying to replicate what Devin does, but exclusively using MultiOn's Agents.

We use 3 separate MultiOn Agents, one each for programming, researching and notetaking.

Their activities are orchestrated and supervised by an overarching GPT-4o

The system prompts for the individual agents and overarching agent can be found in `prompts.py`.

The majority of the execution logic is contained in `DevOn.run()` in the `agent.py` file.
