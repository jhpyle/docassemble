import json

def safe_json_loads(data):
    return json.loads(data.decode("utf-8", "strict"))
