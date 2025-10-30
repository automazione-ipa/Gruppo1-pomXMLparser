"""
Estrae testo pulito, paragrafi, liste e code dai JSON di sezione
"""
import json
from bs4 import BeautifulSoup


def parse_section(section: dict) -> dict:
    soup = BeautifulSoup(section['content'], 'lxml')
    paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
    lists = {
        'ul': [li.get_text(strip=True) for ul in soup.find_all('ul') for li in ul.find_all('li')],
        'ol': [li.get_text(strip=True) for ol in soup.find_all('ol') for li in ol.find_all('li')]
    }
    code = [code.get_text(strip=True) for code in soup.find_all('code')]
    return {
        'id': section['id'],
        'title': section['title'],
        'paragraphs': paragraphs,
        'lists': lists,
        'code': code
    }


if __name__ == '__main__':
    with open('data/sections.json') as f:
        secs = json.load(f)
    parsed = [parse_section(s) for s in secs]
    with open('data/sections_parsed.json', 'w') as f:
        json.dump(parsed, f, indent=2)