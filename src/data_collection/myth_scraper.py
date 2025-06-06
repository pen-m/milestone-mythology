import requests
import os
import json

base_url = "https://thegreekmythapi.vercel.app/api"

endpoints = ['gods', 'titans', 'heroes', 'monsters']

output_dir = "data/greek_mythology"
os.makedirs(output_dir, exist_ok=True)

all_data = {}

for endpoint in endpoints:
    url = f"{base_url}/{endpoint}"
    response = requests.get(url)

    if response.status_code == 200:
        print(f"{endpoint}: {response.status_code}")
        data = response.json()
        all_data[endpoint] = data
        print(f"{endpoint} entries: {len(data)}")

        with open(os.path.join(output_dir, f"{endpoint}.json"), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Saved: {endpoint}.json with {len(data)} records")

all_data.keys()