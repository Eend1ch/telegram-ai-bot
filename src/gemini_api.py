from google import genai
import json

with open("file.json", "r", encoding="UTF-8") as file:
    data = json.load(file)
client = genai.Client(api_key=data["gemini"])


def load_agent(name):
    with open(f"./.agents/{name}/AGENTS.md", encoding="utf-8") as f:
        return f.read()

def gemini_answer(message, agent="default"):
    if agent == "default":
        interaction = client.interactions.create(
            model="gemini-3.5-flash",
            input=message
        )
        return interaction.output_text
    else:
        content = load_agent(agent)
        interaction = client.interactions.create(
            agent="antigravity-preview-05-2026",
            input=message,
            environment={
                "type": "remote",
                "sources": [
                    {
                        "type": "inline",
                        "target": ".agents/AGENTS.md",
                        "content": content,
                    },
                ],
            },
        )

        return interaction.output_text
