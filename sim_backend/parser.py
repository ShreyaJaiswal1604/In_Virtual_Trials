import re
import json

def safe_parse_json(raw: str) -> dict:
    # Strip code fences and isolate the JSON object
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw)
    cleaned = re.sub(r"\s*```$", "", cleaned).strip()
    start = cleaned.find("{")
    end   = cleaned.rfind("}") + 1
    if start < 0 or end < 0:
        raise ValueError("No JSON object found")
    return json.loads(cleaned[start:end])

# These can stay as stubs since we directly parse JSON
def extract_temperature_curve(text: str) -> dict:
    return {}

def extract_activity_loss(text: str) -> dict:
    return {}
