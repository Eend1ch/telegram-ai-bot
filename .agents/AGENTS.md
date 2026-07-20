from google import genai

client = genai.Client()


def create(agent):
    interaction = client.interactions.create(
        agent=agent, 
        input="Analyze the Q1 revenue data and create a report.",
        system_instruction="You are a data analyst. Always include visualizations and export results as PDF.",
        environment={
            "type": "remote",
            "sources": [
                {
                    "type": "inline",
                    "target": ".agents/AGENTS.md",
                    "content": "Always use matplotlib for charts. Include a summary table in every report.",
                },
            ],
        },
    )
    
    return interaction.output_text
