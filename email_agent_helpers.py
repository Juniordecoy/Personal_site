import json
import os

AI_DATA_FOLDER = os.path.join("static", "data", "ai_control_center")


def load_email_agent_config():
    config_path = os.path.join(AI_DATA_FOLDER, "email_agent_config.json")

    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_email_tools():
    tools_path = os.path.join(AI_DATA_FOLDER, "tools", "email_tools.json")

    with open(tools_path, "r", encoding="utf-8") as file:
        return json.load(file)

def load_email_agent_workflow():
    workflow_path = os.path.join(AI_DATA_FOLDER, "email_agent_workflow.json")

    with open(workflow_path, "r", encoding="utf-8") as file:
        return json.load(file)