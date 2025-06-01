from bs4 import BeautifulSoup
import requests
import os
import json
import re


trope_urls = {
    # 1. Narrative Structure Tropes
    "TheHeroJourney": "https://tvtropes.org/pmwiki/pmwiki.php/Main/TheHeroJourney",
    "TheChosenOne": "https://tvtropes.org/pmwiki/pmwiki.php/Main/TheChosenOne",
    "Prophecy": "https://tvtropes.org/pmwiki/pmwiki.php/Main/Prophecy",
    "ProphecyTwist": "https://tvtropes.org/pmwiki/pmwiki.php/Main/ProphecyTwist",
    "FatedToDie": "https://tvtropes.org/pmwiki/pmwiki.php/Main/FatedToDie",
    "FateWorseThanDeath": "https://tvtropes.org/pmwiki/pmwiki.php/Main/FateWorseThanDeath",
    "DarkestHour": "https://tvtropes.org/pmwiki/pmwiki.php/Main/DarkestHour",
    "Apotheosis": "https://tvtropes.org/pmwiki/pmwiki.php/Main/Apotheosis",
    "Reincarnation": "https://tvtropes.org/pmwiki/pmwiki.php/Main/Reincarnation",
    "BornOfMagic": "https://tvtropes.org/pmwiki/pmwiki.php/Main/BornOfMagic",

    # 2. Gods, Creatures, Elementals, Archetypes
    "WarGod": "https://tvtropes.org/pmwiki/pmwiki.php/Main/WarGod",
    "GodOfWar": "https://tvtropes.org/pmwiki/pmwiki.php/Main/GodOfWar",
    "GaiaTheMotherEarth": "https://tvtropes.org/pmwiki/pmwiki.php/Main/GaiaTheMotherEarth",
    "GreenMan": "https://tvtropes.org/pmwiki/pmwiki.php/Main/GreenMan",
    "NatureSpirit": "https://tvtropes.org/pmwiki/pmwiki.php/Main/NatureSpirit",
    "SunGod": "https://tvtropes.org/pmwiki/pmwiki.php/Main/SunGod",
    "MoonGod": "https://tvtropes.org/pmwiki/pmwiki.php/Main/MoonGod",
    "SkyGod": "https://tvtropes.org/pmwiki/pmwiki.php/Main/SkyGod",
    "ElementalPowers": "https://tvtropes.org/pmwiki/pmwiki.php/Main/ElementalPowers",
    "ElementalEmbodiment": "https://tvtropes.org/pmwiki/pmwiki.php/Main/ElementalEmbodiment",
    "GoddessOfFertility": "https://tvtropes.org/pmwiki/pmwiki.php/Main/GoddessOfFertility",
    "TheMother": "https://tvtropes.org/pmwiki/pmwiki.php/Main/TheMother",
    "HearthGoddess": "https://tvtropes.org/pmwiki/pmwiki.php/Main/HearthGoddess",
    "DeathGod": "https://tvtropes.org/pmwiki/pmwiki.php/Main/DeathGod",
    "GodOfTheDead": "https://tvtropes.org/pmwiki/pmwiki.php/Main/GodOfTheDead",
    "GrimReaper": "https://tvtropes.org/pmwiki/pmwiki.php/Main/GrimReaper",
    "GodIsFlawed": "https://tvtropes.org/pmwiki/pmwiki.php/Main/GodIsFlawed",
    "GodIsNeutral": "https://tvtropes.org/pmwiki/pmwiki.php/Main/GodIsNeutral",
    "Shapeshifting": "https://tvtropes.org/pmwiki/pmwiki.php/Main/Shapeshifting",
    "ShapeshifterShowdown": "https://tvtropes.org/pmwiki/pmwiki.php/Main/ShapeshifterShowdown",
    "AnimalMotifs": "https://tvtropes.org/pmwiki/pmwiki.php/Main/AnimalMotifs",
    "TotemGuardian": "https://tvtropes.org/pmwiki/pmwiki.php/Main/TotemGuardian",
    "SpiritAdvisor": "https://tvtropes.org/pmwiki/pmwiki.php/Main/SpiritAdvisor",
    "DragonsAreDivine": "https://tvtropes.org/pmwiki/pmwiki.php/Main/DragonsAreDivine",
    "Phoenix": "https://tvtropes.org/pmwiki/pmwiki.php/Main/Phoenix",
    "SacredBeast": "https://tvtropes.org/pmwiki/pmwiki.php/Main/SacredBeast",
    "BeastMan": "https://tvtropes.org/pmwiki/pmwiki.php/Main/BeastMan",
    "DivineBeast": "https://tvtropes.org/pmwiki/pmwiki.php/Main/DivineBeast",
    "AnthropomorphicDeity": "https://tvtropes.org/pmwiki/pmwiki.php/Main/AnthropomorphicDeity",
    "GodOfChaos": "https://tvtropes.org/pmwiki/pmwiki.php/Main/GodOfChaos",
    "TheTrickster": "https://tvtropes.org/pmwiki/pmwiki.php/Main/TheTrickster",
    "KarmicTrickster": "https://tvtropes.org/pmwiki/pmwiki.php/Main/KarmicTrickster",

    # 3. Moral Symbolism and Good vs Evil
    "TheMessiah": "https://tvtropes.org/pmwiki/pmwiki.php/Main/TheMessiah",
    "WhiteMage": "https://tvtropes.org/pmwiki/pmwiki.php/Main/WhiteMage",
    "BenevolentTrickster": "https://tvtropes.org/pmwiki/pmwiki.php/Main/BenevolentTrickster",
    "WellIntentionedExtremist": "https://tvtropes.org/pmwiki/pmwiki.php/Main/WellIntentionedExtremist",
    "AntiHero": "https://tvtropes.org/pmwiki/pmwiki.php/Main/AntiHero",
    "BigBad": "https://tvtropes.org/pmwiki/pmwiki.php/Main/BigBad",
    "EldritchAbomination": "https://tvtropes.org/pmwiki/pmwiki.php/Main/EldritchAbomination",
    "Satan": "https://tvtropes.org/pmwiki/pmwiki.php/Main/Satan",
    "GodIsGood": "https://tvtropes.org/pmwiki/pmwiki.php/Main/GodIsGood",
    "DealWithTheDevil": "https://tvtropes.org/pmwiki/pmwiki.php/Main/DealWithTheDevil"
}


def scrape_many_tropes(trope_dict, output_dir='data'):
    """Fn to scrape a list of TV Tropes pages
    Input(s):
    Output:
    Exceptions:
    """
    for trope_name, url in trope_dict.items():
        print(f'Scraping {trope_name} from {url})')
        try:
            soup = fetch_page(url)
            description = extract_description(soup)
            examples = extract_examples(soup)

            data = {
                'trope': trope_name.replace('_', ' '),
                'url': url,
                'description': description,
                'examples': examples
            }

            filename = os.path.join(output_dir, f'trope_{trope_name}.json')
            save_json(data, filename)
            print(f'Saved: {filename} \n')

        except Exception as e:
            print(f'Error scraping {trope_name}: {e}\n')


def fetch_page(url):
    """Fn to fetch the HTML content of a TV Tropes page
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

def extract_description(soup):
    """Fn to extract the semantic definition/trope introduction text
    Input(s):
    Output:
    Exceptions:
    """

    #1. Find the main article content
    main_div = soup.find('div', id='main-article')

    #2. Raise an exception if the main content is not found
    if not main_div:
        raise Exception("Main article content not found")
    
    #3. Collect all the paragraph tags until h2<Examples>
    paragraphs = []

    for tag in main_div.find_all(recursive=False):
        if tag.name == 'p':
            paragraphs.append(tag.get_text(strip=True))
        elif tag.name in ['h2', 'hr']:
            break
    
    #4. Combine into one block of text
    description = '\n\n'.join(paragraphs)

    return description

def extract_examples(soup):
    """Fn to extract structured examples of different media types for each trope
    Input(s):
    Output:
    Exceptions:
    """
    main_div = soup.find('div', id='main-article')

    if not main_div:
        raise Exception("Main article content not found")
    
    examples = []
    current_section = None

    #go through all the h2 children of the main div
    for tag in main_div.find_all(['h2', 'div']):
        if tag.name == 'h2':
            #Start a new section
            current_section = tag.get_text(strip=True)
            # print(current_section)
        
        elif tag.name == 'div' and tag.get('class') and 'folder' in tag.get('class') and current_section:
            ul = tag.find('ul')
            if not ul:
                continue
            #collect all the items under the current header
            for li in ul.find_all('li', recursive=False):
                entry_text = li.get_text(strip=True)

                links = []
                for a in li.find_all('a', href=True):
                    links.append({
                        'title': a.get_text(strip=True),
                        'url': a['href']
                    })

                examples.append({
                    'section': current_section,
                    'text': entry_text,
                    'links': links
                })
    return examples


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

    scrape_many_tropes(trope_urls)
    # print('Script is running')
    # url = 'https://tvtropes.org/pmwiki/pmwiki.php/Main/TricksterGod'
    # soup = fetch_page(url)

    # # print(soup.title.string)

    # description = extract_description(soup)

    # examples = extract_examples(soup)
    # #print(f'Found {len(examples)} examples')
    # #print(examples[0])

    # data = {
    #     'trope': 'Trickster God',
    #     'url': url,
    #     'description': description,
    #     'examples': examples
    # }

    # save_json(data, 'data/trope_TricksterGod.json')