from agent import Analyst

if __name__ == "__main__":
    analyst = Analyst(
        "OPENAI_API_KEY",
        "MULTION_API_KEY",
    )
    out = analyst.run(
        business_description="We run a chip business that designs and manufactures AI-specific chips for mobile devices."
    )

    print("The finished analysis is: ")
    print(out)
