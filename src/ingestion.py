"""
Esegue lo scraping del sito e salva sezioni in JSON
"""
import json
import requests
from bs4 import BeautifulSoup
from data.config import settings


def fetch_sections() -> list:
    resp = requests.get(settings.source_url, headers=settings.headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'lxml')
    sections = []
    for header in soup.select('h2'):
        sid = header.get_text(strip=True).lower().replace(' ', '-')
        content = ''
        for sib in header.find_next_siblings():
            if sib.name == 'h2': break
            content += str(sib)
        sections.append({'id': sid, 'title': header.get_text(), 'content': content})
    return sections


if __name__ == '__main__':
    secs = fetch_sections()
    with open('data/sections.json', 'w') as f:
        json.dump(secs, f, indent=2)