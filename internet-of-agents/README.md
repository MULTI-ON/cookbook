# Internet of Agents

Spin up a swarm of AI Agents using MultiOn to accomplish tasks on the web 🚀

## How to run

1. Make sure that the MultiOn Chrome Extension is installed and enabled (for more details, see [here](https://docs.multion.ai/learn/browser-extension)).

2. Create a .env file and store the following variables:

```bash
OPENAI_API_KEY=<your-openai-api-key>
MULTION_API_KEY=<your-multion-api-key>
```

3. Install required packages with poetry:

```bash
poetry install
```

4. Run the social media manager! Make sure that you are logged into LinkedIn, X, and Facebook.

```bash
poetry run python social_manager.py
```
