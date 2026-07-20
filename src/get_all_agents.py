from pathlib import Path

directory = Path('./.agents/')

def get_agents():
    agents = []
    for item in directory.iterdir():
        if item.is_dir():
            agents.append(item.name)
    return agents
