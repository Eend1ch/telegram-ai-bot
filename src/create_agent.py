import os

def add_agent(agent_name, information):
    directory_name = agent_name

    # Создание самой папки
    try:
        os.mkdir(f"./.agents/{directory_name}")
        print(f"Directory '{directory_name}' created successfully.")
        with open(f"./.agents/{directory_name}/AGENTS.md", 'w', encoding="UTF-8") as file:
            file.write(information)

    except FileExistsError:
        print(f"Directory '{directory_name}' already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create '{directory_name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

