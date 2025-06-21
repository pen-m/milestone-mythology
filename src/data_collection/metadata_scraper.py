from imdb import IMDb
import json
import pandas as pd
import requests
from pathlib import Path
import time


combined_path = Path("data/combined_dataset.json")
expanded_path = Path("data/expanded_dataset.json")

combined_df = pd.read_json(combined_path, lines=True)

if expanded_path.exists():
    expanded_df = pd.read_json(expanded_path, lines=True)
    processed_ids = set(expanded_df['id'])
    expanded_entries = expanded_df.to_dict(orient='records')
else:
    processed_ids = set()
    expanded_entries = []

ia = IMDb()

checkpoint_interval = 50
counter = 0

for i, row in combined_df.iterrows():
    if row['id'] in processed_ids:
        continue

    if row['type'] != 'modern_media':
        expanded_entries.append(row.to_dict())
        continue

    entry = row.to_dict()
    title = entry['text'].split(' is ')[0]

    if any(title.lower().startswith(prefix) for prefix in ['list of', 'index of']):
        entry['skip_reason'] = 'generic_title'
        expanded_entries.append(entry)
        continue

    #IMDb lookup
    try:
        print(f"Searching IMDb for {title}")
        imdb_results = ia.search_movie(title)
        time.sleep(0.5)
        if imdb_results:
            media = imdb_results[0]
            ia.update(media)
            entry['imdb_title'] = media.get('title')
            entry['imdb_year'] = media.get('year')
            entry['imdb_genres'] = media.get('genres')
            entry['imdb_plot'] = media.get('plot outline')
    except Exception as e:
        print(f"IMDb error for {title}: {e}")
        entry['imdb_error'] = str(e)

    # Google Books lookup
    try:
        query = title.replace(" ", "+")
        url = f'https://www.googleapis.com/books/v1/volumes?q=intitle:{query}'
        response = requests.get(url)
        time.sleep(0.5)
        if response.status_code == 200:
            items = response.json().get('items')
            if items:
                volume_info = items[0]['volumeInfo']
                entry['book_title'] = volume_info.get('title')
                entry['book_authors'] = volume_info.get('authors')
                entry['book_description'] = volume_info.get('description')
                entry['book_publishedDate'] = volume_info.get('publishedDate')
    except Exception as e:
        entry['books_error'] = str(e)

    # Append and checkpoint
    expanded_entries.append(entry)
    counter += 1

    if counter % checkpoint_interval == 0:
        print(f"Checkpoint reached at {counter} entries. Saving progress...")
        pd.DataFrame(expanded_entries).to_json(expanded_path, orient='records', lines=True, force_ascii=False)

# Final save
print("Saving final dataset...")
pd.DataFrame(expanded_entries).to_json(expanded_path, orient='records', lines=True, force_ascii=False)
print("Done.")

# for i, row in combined_df.iterrows():
#     if row['type'] != 'modern_media':
#         expanded_entries.append(row.to_dict())
#         continue

#     entry = row.to_dict()
#     title = entry['text'].split(' is ')[0]

# #https://www.geeksforgeeks.org/python-imdbpy-searching-a-movie/
#     try:
#         print(f'Searching IMDb for {title}')
#         imdb_results = ia.search_movie(title)
#         time.sleep(0.5)
#         if imdb_results:
#             media = imdb_results[0]
#             ia.update(media)
#             entry['imdb_title'] = media.get('title')
#             entry['imdb_year'] = media.get('year')
#             entry['imdb_genres'] = media.get('genres')
#             entry['imdb_plot'] = media.get('plot outline')
#     except Exception as e:
#         print(f'IMDb error for {title}: {e}')
#         entry['imdb_error'] = str(e)

#     try:
#         query = title.replace(" ", "+")
#         url = f'https://www.googleapis.com/books/v1/volumes?q=intitle:{query}'
#         response = requests.get(url)
#         time.sleep(0.5)
#         if response.status_code == 200:
#             items = response.json().get('items')
#             if items:
#                 volume_info = items[0]['volumeInfo']
#                 entry['book_title'] = volume_info.get('title')
#                 entry['book_authors'] = volume_info.get('authors')
#                 entry['book_description'] = volume_info.get('description')
#                 entry['book_publishedDate'] = volume_info.get('publishedDate')
#     except Exception as e:
#         entry['books_error'] = str(e)

#     expanded_entries.append(entry)

# expanded_df = pd.DataFrame(expanded_entries)

# expanded_df.to_json(expanded_path, orient='records', lines=True, force_ascii=False)

# print(expanded_df.head(10))



