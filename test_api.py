import sys
import json
from datetime import datetime
import requests

BASE_URL = "http://localhost:8000"

def build_payload(schema_doc, operation, custom_context):
    """Inspects OpenAPI schema to build the exact JSON body expected by the route."""
    req_body = operation.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema", {})
    ref = req_body.get("$ref", "")
    if not ref:
        return {"action_context": custom_context}

    schema_name = ref.split("/")[-1]
    props = schema_doc.get("components", {}).get("schemas", {}).get(schema_name, {}).get("properties", {})
    payload = {}

    for field, meta in props.items():
        if "context" in field:
            payload[field] = custom_context
        elif "hour" in field:
            payload[field] = datetime.now().hour
        elif "url" in field:
            payload[field] = "https://example.com"
        elif meta.get("type") == "integer":
            payload[field] = 1
        else:
            payload[field] = custom_context

    return payload

def run_all_tests(custom_context):
    schema_resp = requests.get(f"{BASE_URL}/openapi.json")
    schema_resp.raise_for_status()
    schema_doc = schema_resp.json()
    paths = schema_doc.get("paths", {})

    print(f"Discovered {len(paths)} endpoints on {BASE_URL}\n" + "=" * 50)

    for path, methods in paths.items():
        for method, operation in methods.items():
            url = f"{BASE_URL}{path}"
            print(f"\n>>> Testing {method.upper()} {path}")

            try:
                if method.lower() == "get":
                    params = {"limit": 5} if "journal" in path else {}
                    resp = requests.get(url, params=params)
                elif method.lower() == "post":
                    payload = build_payload(schema_doc, operation, custom_context)
                    print(f"Payload: {json.dumps(payload)}")
                    resp = requests.post(url, json=payload)
                else:
                    continue

                print(f"Status: {resp.status_code}")
                print(json.dumps(resp.json(), indent=2))
            except Exception as err:
                print(f"Request error on {path}: {err}")

if __name__ == "__main__":
    context_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Automated schema-aware API test"
    try:
        run_all_tests(context_input)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to http://localhost:8000. Make sure a server is running.")
