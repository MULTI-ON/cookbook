from agent import Agent

if __name__ == "__main__":
    agent = Agent(
        "OPENAI_API_KEY",
        "MULTION_API_KEY",
    )
    out = agent.run(
        user_info="I am a recent cs grad with 2 internships. Help me find a SWE Job."
    )

    print(
        "I have finished the process of looking for and applying to suitable jobs. The final output is:"
    )
    print(out)
