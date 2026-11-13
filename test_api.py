import sys
import json
import requests

BASE_URL = "http://localhost:8000"

def run_all_tests(custom_context):
    # 1. Fetch the live OpenAPI schema to discover all endpoints
    schema_resp = requests.get(f"{BASE_URL}/openapi.json")
    schema_resp.raise_for_status()
    paths = schema_resp.json().get("paths", {})

    print(f"Discovered {len(paths)} endpoints on {BASE_URL}\n" + "=" * 50)

    # 2. Loop through every endpoint and method
    for path, methods in paths.items():
        for method in methods.keys():
            url = f"{BASE_URL}{path}"
            print(f"\n>>> Testing {method.upper()} {path}")

            try:
                if method.lower() == "get":
                    params = {"limit": 5} if "journal" in path else {}
                    resp = requests.get(url, params=params)
                elif method.lower() == "post":
                    payload = {"action_context": custom_context}
                    resp = requests.post(url, json=payload)
                else:
                    print(f"Skipping unsupported HTTP method: {method.upper()}")
                    continue

                print(f"Status: {resp.status_code}")
                print(json.dumps(resp.json(), indent=2))
            except Exception as err:
                print(f"Request error on {path}: {err}")

if __name__ == "__main__":
    # Use command-line text if provided, otherwise fall back to a default string
    context_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Automated full-suite check"

    try:
        run_all_tests(context_input)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to http://localhost:8000. Make sure monolith.py is running.")
