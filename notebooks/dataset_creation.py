import os
import json
import pandas as pd
from pathlib import Path

mythology_dir = Path("data/greek_mythology")
wikipedia_dir = Path("data")

filenames = ['gods.json', 'titans.json', 'heroes.json', 'monsters.json']

myth_data = []
for filename in filenames:
    filepath = mythology_dir / filename
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

            if isinstance(data, dict):
                entities = list(data.values())[0]  # Get the list under the only key
            else:
                print(f"Unexpected structure in {filename}")
                continue

            for entry in entities:
                if isinstance(entry, dict):
                    name = entry.get('name', '')
                    description = entry.get('description', '')
                    symbols = entry.get('attributes', {}).get('symbols', [])
                    symbols_str = ', '.join(symbols) if isinstance(symbols, list) else str(symbols)

                    myth_data.append({
                        "id": f"{filename.replace('.json','')}_{name.lower().replace(' ', '_')}",
                        "text": f"{name} is {description} Symbols: {symbols_str}",
                        "type": "mythological_figure",
                        "source": filename.replace('.json','')
                    })
                else:
                    print(f"Skipping non-dict entry in {filename}: {entry}")


wiki_data = []
for file in wikipedia_dir.glob('wiki_*.json'):
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        title = data.get('title', '')
        for thing in data.get('examples', []):
            name =  thing.get('title', '')
            category = thing.get('category', '')
            url = thing.get('url', '')
            text = f'{name} is a {title} from wikipedia. More info: {url}'
            wiki_data.append({
                'id': f'media_{name.lower().replace(' ', '')}',
                'text': text,
                'type': 'modern_media',
                'source': title
            })

combined_data = pd.DataFrame(myth_data + wiki_data)

#print(wiki_data[:10])

print(myth_data[:10])

#print(combined_data.head(10))

combined_data.to_json('data/combined_dataset.json', orient='records', lines=True, force_ascii=False)