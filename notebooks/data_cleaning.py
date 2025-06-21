import json
import pandas as pd
import numpy as np
from difflib import SequenceMatcher
from itertools import chain





# print(df.shape)
# print(df.columns.tolist())
# print(df.sample(5))

#shape: (2475, 14)
#columns: ['id', 'text', 'type', 'source', 'imdb_title', 'imdb_year', 'imdb_genres', 'imdb_plot',
# 'book_title', 'book_authors', 'book_description', 'book_publishedDate', 'skip_reason', 'imdb_error']

# print(df.dtypes)
# print(df.isna().sum().sort_values(ascending=False))
# id                     object
# text                   object
# type                   object
# source                 object
# imdb_title             object
# imdb_year             float64
# imdb_genres            object
# imdb_plot              object
# book_title             object
# book_authors           object
# book_description       object
# book_publishedDate     object
# skip_reason            object
# imdb_error             object
# dtype: object
# imdb_error            2474
# skip_reason           2449
# imdb_plot             1285
# book_description       861
# imdb_genres            563
# book_authors           483
# book_publishedDate     414
# imdb_year              342
# book_title             332
# imdb_title             289
# id                       0
# text                     0
# type                     0
# source                   0
# dtype: int64

# #check if the missing values make sense (i.e. imdb_year is missing for non-movies/non-tv shows)
# # Filter modern media entries with missing imdb_title
# missing_imdb = df[(df['type'] == 'modern_media') & (df['imdb_title'].isna())]

# # Count by source for entries missing imdb info
# imdb_missing_by_source = missing_imdb['source'].value_counts()

# # Filter modern media entries with missing book_title
# missing_books = df[(df['type'] == 'modern_media') & (df['book_title'].isna())]

# # Count by source for entries missing book info
# books_missing_by_source = missing_books['source'].value_counts()

# print("IMDb entries with missing title: ", missing_imdb)
# print("Entries that don't have IMDb data: ", imdb_missing_by_source)
# print("Book entries with missing title: ", missing_books)
# print("Entries that don't have book data: ", books_missing_by_source)

# IMDb entries with missing title:                                                 id  ...                                         imdb_error
# 201                 media_listofacesfdoubletitles  ...                                               None
# 202    media_listofacesfletter-seriessingletitles  ...                                               None
# 203   media_listofacesfnumeric-seriessingletitles  ...                                               None
# 226                          media_canopusinargos  ...                                               None
# 229                      media_christclonetrilogy  ...                                               None
# ...                                           ...  ...                                                ...
# 2213                 media_listofstorycollections  ...                                               None
# 2251                      media_mythopoeicsociety  ...                                               None
# 2375                                      media_e  ...  {'errcode': None, 'errmsg': 'None', 'url': 'ht...
# 2421              media_australianmusictelevision  ...                                               None
# 2459                     media_kirikou(videogame)  ...                                               None

# [89 rows x 14 columns]
# Entries that don't have IMDb data:  source
# Fantasy films                         20
# Science fiction book series           18
# Fantasy tv programs                   17
# High fantasy works                    12
# 2000s scifi novels                     4
# Films based on classical mythology     4
# Mythopoeia                             3
# 1990s scifi novels                     2
# Science fiction novels                 2
# Fantasy television series              2
# 1990s American scifi tv                1
# Supernatural television series         1
# 2000s American scifi tv                1
# 2000s British scifi tv                 1
# Video games based on mythology         1
# Name: count, dtype: int64
# Book entries with missing title:                                                 id                                               text  ...    skip_reason imdb_error
# 201                 media_listofacesfdoubletitles  List of Ace SF double titles is a Science fict...  ...  generic_title       None
# 202    media_listofacesfletter-seriessingletitles  List of Ace SF letter-series single titles is ...  ...  generic_title       None
# 203   media_listofacesfnumeric-seriessingletitles  List of Ace SF numeric-series single titles is...  ...  generic_title       None
# 216             media_aliettedebodardbibliography  Aliette de Bodard bibliography is a Science fi...  ...           None       None
# 312                           media_ilium/olympos  Ilium/Olympos is a Science fiction book series...  ...           None       None
# ...                                           ...                                                ...  ...            ...        ...
# 2438       media_benjordan:paranormalinvestigator  Ben Jordan: Paranormal Investigator is a Video...  ...           None       None
# 2443                  media_bō:pathoftheteallotus  Bō: Path of the Teal Lotus is a Video games ba...  ...           None       None
# 2456                               media_dreadout  DreadOut is a Video games based on mythology f...  ...           None       None
# 2467                  media_serpentinthestaglands  Serpent in the Staglands is a Video games base...  ...           None       None
# 2474                              media_wizard101  Wizard101 is a Video games based on mythology ...  ...           None       None

# [132 rows x 14 columns]
# Entries that don't have book data:  source
# Fantasy tv programs                   67
# Fantasy films                         19
# High fantasy works                    15
# Films based on classical mythology     8
# Science fiction book series            6
# Video games based on mythology         6
# 1990s American scifi tv                3
# 2000s British scifi tv                 3
# Fantasy television series              2
# 2000s American scifi tv                1
# Science fiction novels                 1
# Mythopoeia                             1
# Name: count, dtype: int64

#What does this mean?
#the entries that don't have book/imdb titles are mostly wikipedia categories that wouldn't have data and should be deleted from the dataset
#there aren't that many, so it looks like I got metadata for most of the wikipedia entries

#it looks like the imdb API looked for the closest title match, even if it wasn't exact
#for example, the Book 'Acorna' was matched to the British TV series 'Acorn Antiques'
#need to do a similarity check

manual_overrides = {
    'blasphemous(videogame)': 'Blasphemous',
    'shazam!(film)': 'Shazam!',
    # etc.
}

def media_format_from_id(row):
    if not isinstance(row['id'], str):
        return None
    id_lower = row['id'].lower()
    if 'videogame' in id_lower or 'video_game' in id_lower or 'game' in id_lower:
        return 'game'
    elif 'film' in id_lower or 'tv' in id_lower or 'series' in id_lower:
        return 'screen'
    elif 'book' in id_lower or 'novel' in id_lower or 'comic' in id_lower or 'manga' in id_lower:
        return 'book'
    return None


def clean_title(text):
    # Removes brackets, subtitles, etc.
    if not isinstance(text, str):
        return ''
    return (
        text.lower()
        .replace('(tv series)', '')
        .replace('(series)', '')
        .replace('(miniseries)', '')
        .replace('[1]', '')  # remove citation refs
        .replace('’', "'")
        .replace('“', '"').replace('”', '"')
        .replace(':', '')
        .strip()
    )


def should_skip(text):
    if not isinstance(text, str):
        return False
    lowered = text.lower()
    return lowered.startswith("list of") or any(
        skip_term in lowered for skip_term in [
            'franchise', 'universe', 'movement', 'society', 'chronologies', 'collection'
        ]
    )

def close_match(original, found, threshold=0.725):
    ratio = SequenceMatcher(None, clean_title(original), clean_title(found)).ratio()
    if ratio > threshold: 
        return True
    else:
        return False


def validate_imdb_match(row):
    if row['type'] != 'modern_media':
        return row
    
    original_title = row['text'].split(' is ')[0].strip()
    imdb_title = row.get('imdb_title')
    media_format = media_format_from_id(row)

    if pd.notna(imdb_title):
        if not close_match(original_title, imdb_title):
            if media_format !='screen' and media_format != 'game':
                row['imdb_title'] = None
                row['imdb_year'] = None
                row['imdb_genres'] = None
                row['imdb_plot'] = None
                row['imdb_error'] = 'low similarity match'
    
    return row



def validate_book_match(row):
    if row['type'] != 'modern_media':
        return row
    
    original_title = row['text'].split(' is ')[0].strip()
    book_title = row.get('book_title')
    media_format = media_format_from_id(row)

    if pd.notna(book_title):
        if not close_match(original_title, book_title):
            if media_format != 'book':
                row['book_title'] = None
                row['book_authors'] = None
                row['book_description'] = None
                row['book_publishedDate'] = None
                row['skip_reason'] = row.get('skip_reason') or 'low similarity book match'
    
    return row


def suspect_format(row):
    """
    Returns True if the entry is likely to need manual review
    due to ambiguous or inconsistent media source.
    """
    if row['source'].lower() == 'mythopoeia':
        return True
    if row['imdb_title'] is None and row['book_title'] is None:
        return True
    return False



def infer_media_type(row):
    
    #print("text: ", row.get('text'), "imdb title: ", row.get('imdb_title'), "book title", row.get('book_title'))

    if row.get('skip_reason') == 'generic_title' or row['text'].lower().startswith('list of'):
        return 'skip'
    elif pd.notna(row.get('imdb_title')) and pd.isna(row.get('book_title')):
        return 'screen'
    elif pd.notna(row.get('book_title')) and pd.isna(row.get('imdb_title')):
        return 'book'
    elif pd.notna(row.get('imdb_title')) and pd.notna(row.get('book_title')):
        return 'both'
    else:
        #print('id: ', row.get('id'), 'imdb title: ', row.get('imdb_title'), 'book title: ', row.get('book_title'))
        return 'unknown'

df = pd.read_json('data/expanded_dataset.json', lines=True, orient='records')


df = df.apply(validate_imdb_match, axis=1)
df = df.apply(validate_book_match, axis=1)

df['inferred_media_type'] = df.apply(infer_media_type, axis=1)
df['suspect_format'] = df.apply(suspect_format, axis=1)
#print(df['inferred_media_type'].value_counts())

##print(df[df['inferred_media_type'] == 'both'].head())

df.to_json("data/cleaned_expanded_dataset.json", orient='records', lines=True, force_ascii=False)

#known problems with the data that was scraped from wikipedia in identifying the media type - Mythopoeia as a catchall term
#return to this to clarify tv/videogames vs books if needed
#return to this to clarify types and continue to clean data if needed

#moving on to next steps in data cleaning - normalizing categorical fields
df['source'] = df['source'].str.strip().str.lower()
df['source'] = df['source'].str.title()

def normalize_genres(genre_list):
    if isinstance(genre_list, list):
        sorted_list = sorted([g.strip().lower() for g in genre_list if isinstance(g, str)])
        return sorted_list
    else:
        return None
    
df['imdb_genres'] = df['imdb_genres'].apply(normalize_genres)

def normalize_authors(author_list):
    if isinstance(author_list, list):
        sorted_list = sorted([a.strip() for a in author_list if isinstance(a, str)])
        return sorted_list
    else:
        return None
    
df['book_authors'] = df['book_authors'].apply(normalize_authors)

# print(df['book_authors'].sample(10))
# print(df['imdb_genres'].sample(10))



all_genres = list(chain.from_iterable(df['imdb_genres'].dropna()))
#print("Top genres:", pd.Series(all_genres).value_counts().head(10))

all_authors = list(chain.from_iterable(df['book_authors'].dropna()))
#print("Top authors:", pd.Series(all_authors).value_counts().head(10))

# Book date: convert string to datetime (year-month-day if possible)
df['book_publishedDate'] = pd.to_datetime(df['book_publishedDate'], errors='coerce', format='mixed')

# IMDb year: cast to integer where possible
df['imdb_year'] = pd.to_numeric(df['imdb_year'], errors='coerce').dropna().astype('Int64')

df['book_year'] = df['book_publishedDate'].dt.year

# print("Valid IMDb year entries:", df['imdb_year'].notna().sum())
# print("Valid book published dates:", df['book_publishedDate'].notna().sum())

# # Optional: If you extracted year from book_publishedDate
# if 'book_year' in df.columns:
#     print("Valid extracted book year entries:", df['book_year'].notna().sum())

    # Initialize the data_quality_flag column
df["data_quality_flag"] = [[] for _ in range(len(df))]

# Helper function to append flags
def append_flag(index, flag):
    df.at[index, "data_quality_flag"].append(flag)

# Flag out-of-range imdb_year
for idx, year in df["imdb_year"].dropna().items():
    if year < 1990 or year > 2026:
        append_flag(idx, "imdb_year_out_of_range")

# Flag out-of-range book_publishedDate
for idx, year in df["book_publishedDate"].dropna().items():
    try:
        y = int(str(year)[:4])
        if y < 1990 or y > 2026:
            append_flag(idx, "book_year_out_of_range")
    except:
        append_flag(idx, "book_year_invalid")

# Flag empty author and genre lists
for idx, authors in df["book_authors"].items():
    if isinstance(authors, list) and len(authors) == 0:
        append_flag(idx, "empty_book_authors")

for idx, genres in df["imdb_genres"].items():
    if isinstance(genres, list) and len(genres) == 0:
        append_flag(idx, "empty_imdb_genres")

# Flag short or placeholder descriptions
for idx, desc in df["book_description"].items():
    if isinstance(desc, str) and (len(desc) < 20 or "no description" in desc.lower()):
        append_flag(idx, "suspicious_book_description")

for idx, plot in df["imdb_plot"].items():
    if isinstance(plot, str) and (len(plot) < 20 or "add a plot" in plot.lower()):
        append_flag(idx, "suspicious_imdb_plot")

# Save updated dataset
df.to_json("data/flagged_cleaned_expanded_dataset.json", orient="records", lines=True, force_ascii=False)

#print(df['data_quality_flag'].explode().value_counts())

#for filtering purposes, create a boolean column indicating if the entry is clean
df['is_clean'] = df['data_quality_flag'].apply(lambda x: len(x) == 0)

# Suggestion 1: Summarize data quality issues by inferred_media_type
flag_counts_by_type = df.explode('data_quality_flag').groupby('inferred_media_type')['data_quality_flag'].value_counts().unstack(fill_value=0)

# Suggestion 3: Profile distributions within is_clean == True
df['is_clean'] = df['data_quality_flag'].apply(lambda x: len(x) == 0)

# For clean entries only
clean_df = df[df['is_clean'] == True]

df.loc[df['is_clean'], 'num_genres'] = df.loc[df['is_clean'], 'imdb_genres'].apply(lambda x: len(x) if isinstance(x, list) else 0)
df.loc[df['is_clean'], 'num_authors'] = df.loc[df['is_clean'], 'book_authors'].apply(lambda x: len(x) if isinstance(x, list) else 0)

# Distribution of years
imdb_year_dist = clean_df['imdb_year'].dropna()
book_year_dist = clean_df['book_publishedDate'].dropna()

import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6])
plt.show()