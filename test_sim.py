import requests
import json

url = "http://localhost:8000/simulation/run"

# Mock Payload simulating "Auto-Select" machine (machine_id: None)
payload = {
  "material_id": 1,
  "machine_id": None,
  "geometry_stats": {
    "volume_mm3": 15000,
    "projected_area_mm2": 5000,
    "bbox": {"x": 100, "y": 50, "z": 30}
  },
  "flow_length_mm": None
}

try:
    print(f"Sending payload: {json.dumps(payload, indent=2)}")
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
