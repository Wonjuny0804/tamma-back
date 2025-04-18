import os
import json

TEMPLATES_PATH = "app/templates"

def load_template_config(template_id: str) -> dict:
    path = os.path.join(TEMPLATES_PATH, template_id, "config.json")
    return json.load(open(path))

def load_prompt(template_id: str) -> str:
    path = os.path.join(TEMPLATES_PATH, template_id, "prompt.txt")
    return open(path).read()

def load_scaffold_code(template_id: str) -> str:
    path = os.path.join(TEMPLATES_PATH, template_id, "scaffold.py")
    return open(path).read()

def generate_feature_code(template_id: str, user_inputs: dict) -> dict:
    prompt_template = load_prompt(template_id)
    filled_prompt = prompt_template.format(**user_inputs)
    scaffold_code = load_scaffold_code(template_id)

    return {
        "prompt": filled_prompt,
        "code": scaffold_code
    }
