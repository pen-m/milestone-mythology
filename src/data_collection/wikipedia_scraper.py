from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin, urldefrag
import requests
import os
import json
import re


wiki_urls = {
    # TV Series
    "Fantasy tv programs": "https://en.wikipedia.org/wiki/List_of_fantasy_television_programs",
    "1990s American scifi tv": "https://en.wikipedia.org/wiki/Category:1990s_American_science_fiction_television_series",
    "Fantasy television series": "https://en.wikipedia.org/wiki/Category:Fantasy_television_series",
    "TV series based on mythology": "https://en.wikipedia.org/wiki/Category:Television_series_based_on_mythology",
    "Supernatural television series": "https://en.wikipedia.org/wiki/Category:Supernatural_television_series",
    "Urban fantasy television series": "https://en.wikipedia.org/wiki/Category:Urban_fantasy_television_series",

    # Film
    "Fantasy films": "https://en.wikipedia.org/wiki/List_of_fantasy_films",
    "Fantasy film category": "https://en.wikipedia.org/wiki/Category:Fantasy_films",
    "Films based on classical mythology": "https://en.wikipedia.org/wiki/Category:Films_based_on_classical_mythology",
    "Mythopoeia": "https://en.wikipedia.org/wiki/Category:Mythopoeia",

    # Literature
    "High fantasy works": "https://en.wikipedia.org/wiki/List_of_high_fantasy_works",
    "Fantasy novels by series": "https://en.wikipedia.org/wiki/Category:Fantasy_novels_by_series",
    "Novels based on mythology": "https://en.wikipedia.org/wiki/Category:Novels_based_on_mythology",

    # Games and other media
    "Fantasy video games": "https://en.wikipedia.org/wiki/List_of_fantasy_video_games",
    "Video games based on mythology": "https://en.wikipedia.org/wiki/Category:Video_games_based_on_mythology",

    # 1990s Sci-Fi TV
    "1990s American scifi tv": "https://en.wikipedia.org/wiki/Category:1990s_American_science_fiction_television_series",
    "1990s British scifi tv": "https://en.wikipedia.org/wiki/Category:1990s_British_science_fiction_television_series",
    "1990s animated scifi tv": "https://en.wikipedia.org/wiki/Category:1990s_animated_science_fiction_television_series",

    # 2000s Sci-Fi TV
    "2000s American scifi tv": "https://en.wikipedia.org/wiki/Category:2000s_American_science_fiction_television_series",
    "2000s British scifi tv": "https://en.wikipedia.org/wiki/Category:2000s_British_science_fiction_television_series",
    "2000s animated scifi tv": "https://en.wikipedia.org/wiki/Category:2000s_animated_science_fiction_television_series",

    # Sci-Fi Book Series & Novels
    "Science fiction book series": "https://en.wikipedia.org/wiki/Category:Science_fiction_book_series",
    "Science fiction novels": "https://en.wikipedia.org/wiki/Category:Science_fiction_novels",
    "1990s scifi novels": "https://en.wikipedia.org/wiki/Category:1990s_science_fiction_novels",
    "2000s scifi novels": "https://en.wikipedia.org/wiki/Category:2000s_science_fiction_novels",
    "Science fiction novels by series": "https://en.wikipedia.org/wiki/Category:Science_fiction_novels_by_series"


}


def scrape_many_wikis(wiki_dict, output_dir='data'):
    """Fn to scrape a list of Wikipedia pages
    Input(s):
    Output:
    Exceptions:
    """
    for media_name, url in wiki_dict.items():
        print(f'Scraping {media_name} from {url})')
        try:
            soup = fetch_page(url)
            examples = extract_examples(soup)

            data = {
                'title': media_name.replace('_', ' '),
                'url': url,
                'examples': examples
            }

            filename = os.path.join(output_dir, f'wiki_{media_name}.json')
            save_json(data, filename)
            print(f'Saved: {filename} \n')

        except Exception as e:
            print(f'Error scraping {media_name}: {e}\n')


def fetch_page(url):
    """Fn to fetch the HTML content of a wikipedia page
    Input(s):
    Output:
    Exceptions:
    """
    headers = {
        'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/91.0.4472.124 Safari/537.36'
                       )
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch page: {url} (Status code: {response.status_code})")

    return BeautifulSoup(response.text, 'html.parser')


def extract_from_category_page(soup):
    """Fn to extract examples from a category page
    Input(s):
    Output:
    Exceptions:
    """
    examples = []

    category_div = soup.find('div', id='mw-pages')
    if not category_div:
        return []

    for li in category_div.find_all('li'):
        a = li.find('a', href=True)
        if a:
            title = a.get_text(strip=True)
            href = a['href']
            if title and href.startswith('/wiki/') and not href.startswith('wiki/File:') and not href.startswith('/wiki/Template'):
                url = urldefrag(urljoin("http://en.wikipedia.org", href))[0]
                examples.append({
                    'title': title,
                    'url': url
                })

        
    return examples
    
def extract_from_list_page(soup):
    """Fn to extract examples from a list page
    Input(s):
    Output:
    Exceptions:
    """
    
    content_div = soup.find('div', class_='mw-parser-output')
    if not content_div:
        raise Exception('Content area not found')
    
    examples = []
    current_category = None

    for tag in content_div.find_all(['h2', 'ul']):
        if tag.name == 'h2':
            span = tag.find('span', class_='mw-headline')
            if span:
                current_category = span.get_text(strip=True)
        
        elif tag.name == 'ul':
            category_name = current_category if current_category else 'Uncategorized'
            for li in tag.find_all('li', recursive=False):
                a = li.find('a', href=True)
                if a:
                    title = a.get_text(strip=True)
                    href = a['href']
                    if title and href.startswith('/wiki/') and not href.startswith('wiki/File:') and not href.startswith('/wiki/Template'):
                        url = urldefrag(urljoin("http://en.wikipedia.org", href))[0]
                        examples.append({
                        'title': title,
                        'url': url,
                        'category': category_name
                    })
        
    return examples

def extract_examples(soup):
    """Fn to extract all the media examples from the wikipedia page
    Input(s):
    Output:
    Exceptions:
    """

    category_data = extract_from_category_page(soup)
    if category_data:
        return category_data
    
    return extract_from_list_page(soup)

def save_json(data, filename):
    """Fn to save the extracted data to a JSON file
    Input(s):
    Output:
    Exceptions:
    """

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

#pipeline code
if __name__ == "__main__":

    scrape_many_wikis(wiki_urls)


