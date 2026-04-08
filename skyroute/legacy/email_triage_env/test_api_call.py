import requests
import json

url = "http://localhost:7860/step"
# Payload matches the user's provided structure
payload = {
    "action": {
        "action_type": "ListEmails",
        "args": {
            "folder": "INBOX"
        }
    }
}

header = {"Content-Type": "application/json"}

# Reset session
requests.post("http://localhost:7860/reset")

print(f"Sending formatted action: {json.dumps(payload, indent=2)}")
response = requests.post(url, json=payload, headers=header)
print("\nResponse from API:")
print(json.dumps(response.json(), indent=2))
