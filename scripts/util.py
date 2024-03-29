import json


def get_data():
    with open("data/projects.json", "r", encoding="utf-8") as f:
        return json.loads(f.read())


def get_default_slug(mod):
    return mod['slug'] if type(mod['slug']) is str else mod['slug']['mr']
