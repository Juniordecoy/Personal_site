import json
import os


AI_DATA_FOLDER = os.path.join("static", "data", "ai_control_center")


def load_agents():
    agents_path = os.path.join(AI_DATA_FOLDER, "agents.json")

    with open(agents_path, "r", encoding="utf-8") as file:
        return json.load(file)

def load_agent_locations():
    locations_path = os.path.join(AI_DATA_FOLDER, "agent_locations.json")

    with open(locations_path, "r", encoding="utf-8") as file:
        return json.load(file)

def load_system_state():
    system_path = os.path.join(AI_DATA_FOLDER, "system_state.json")

    with open(system_path, "r", encoding="utf-8") as file:
        return json.load(file)

def load_events():
    events_path = os.path.join(AI_DATA_FOLDER, "events.json")

    with open(events_path, "r", encoding="utf-8") as file:
        return json.load(file)

def load_tools_registry():
    tools_path = os.path.join(AI_DATA_FOLDER, "tools_registry.json")

    with open(tools_path, "r", encoding="utf-8") as file:
        return json.load(file)

def load_review_queue():
    review_path = os.path.join(AI_DATA_FOLDER, "review_queue.json")

    with open(review_path, "r", encoding="utf-8") as file:
        return json.load(file)

def load_tasks():
    tasks_path = os.path.join(AI_DATA_FOLDER, "tasks.json")

    with open(tasks_path, "r", encoding="utf-8") as file:
        return json.load(file)