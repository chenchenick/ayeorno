import requests
import json
from datetime import datetime

# API base URL and endpoint
base_url = "https://api.congress.gov/v3"
endpoint = "/bill"

# Query parameters
params = {
    'fromDateTime': '2004-01-01T00:00:00Z',
    'toDateTime': '2024-10-01T23:59:59Z',
    'format': 'json',
    'limit': 250,  # Adjust as needed, max is 250
    'offset': 0,
    'api_key': '83LcYxrjemvuhcQdYqRppczH6njWYyPMnEviFJ8T'
}

# Make the API request
response = requests.get(f"{base_url}{endpoint}", params=params)

if response.status_code == 200:
    bills = response.json()
    
    # Generate a filename with current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"bills_{timestamp}.json"
    
    # Save the bills data to a JSON file
    with open(filename, 'w') as f:
        json.dump(bills, f, indent=4)
    
    print(f"Bills data saved to {filename}")
else:
    print(f"Error: {response.status_code}")
    print(f"Response: {response.text}")
