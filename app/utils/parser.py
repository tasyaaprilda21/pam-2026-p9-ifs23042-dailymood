import json
import re

def parse_llm_response(result):
    try:
        content = result.get("response") or result
        content = re.sub(r"```json\n|\n```", "", content)
        parsed = json.loads(content)
        return parsed
    except Exception as e:
        raise Exception(f"Invalid JSON from LLM: {str(e)}")