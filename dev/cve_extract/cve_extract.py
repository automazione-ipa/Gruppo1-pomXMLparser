import asyncio
import base64
import requests
from playwright.async_api import async_playwright
from packaging import version


OSS_INDEX_TOKEN = "tokenXYZ"


def ossindex_search_maven(group_id, artifact_id, version):
    url = "https://ossindex.sonatype.org/api/v3/component-report"
    coordinates = f"pkg:maven/{group_id}/{artifact_id}@{version}"
    headers = {
        "Authorization": "Basic " + base64.b64encode(
            f"{OSS_INDEX_TOKEN}:".encode()).decode(),
        "Content-Type": "application/json"
    }
    payload = {"coordinates": [coordinates]}
    try:
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code == 200:
            data = r.json()
            return data[0].get("vulnerabilities", [])
        else:
            return [{"title": "Errore API", "reference": url, "cvssScore": "?",
                     "cve": "?", "error": r.text}]
    except Exception as e:
        return [
            {"title": "Errore richiesta", "reference": url, "cvssScore": "?",
             "cve": "?", "error": str(e)}]


def versione_in_range_semantic(versione_target, start, end):
    """
    Controlla se versione_target è >= start e < end usando confronto semantico
    """
    try:
        return version.parse(start) <= version.parse(versione_target) < version.parse(end)
    except Exception:
        return False


async def main(search_term, versione_target):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        search_url = f"https://nvd.nist.gov/vuln/search/results?query={search_term}&search_type=all"
        await page.goto(search_url)

        await page.wait_for_selector('table[data-testid="vuln-results-table"]', timeout=60000)

        links = await page.eval_on_selector_all(
            'table[data-testid="vuln-results-table"] tbody tr th a',
            'els => els.map(e => e.href)'
        )
        print(f"Trovate {len(links)} CVE per '{search_term}'")

        for link in links:
            print(f"\n— Controllo {link}")
            await page.goto(link)

            try:
                await page.wait_for_selector('div#vulnCpeTree', timeout=15000)
            except Exception:
                print("❌ Sezione CPE non trovata, salto.")
                continue

            rows = await page.query_selector_all('div#vulnCpeTree table tr.vulnerable')

            trovata = False

            for row in rows:
                try:
                    cpe_uri = await row.eval_on_selector('td b', 'el => el.innerText')

                    start_el = await row.query_selector('td[data-testid$="-start-range"] b')
                    end_el   = await row.query_selector('td[data-testid$="-end-range"] b')

                    if not start_el or not end_el:
                        print(f"⚠️  Range non trovato per {cpe_uri}, riga ignorata.")
                        continue

                    start = await start_el.inner_text()
                    end   = await end_el.inner_text()

                    # Pulisce "From (including)\n5.0.0" -> "5.0.0"
                    start = start.splitlines()[-1]
                    end = end.splitlines()[-1]

                    if versione_in_range_semantic(versione_target, start, end):
                        print(f"⚠️ {versione_target} ∈ [{start}, {end})  — URI: {cpe_uri}")
                        trovata = True
                except Exception as e:
                    print(f"⚠️  Errore nella riga CPE: {e}")
                    continue

            if not trovata:
                print(f"✅ Nessun intervallo trovato per cui {versione_target} rientra.")

        await browser.close()


if __name__ == "__main__":
    import sys
    term = sys.argv[1] if len(sys.argv) > 1 else "neo4j"
    ver = sys.argv[2] if len(sys.argv) > 2 else "2.14.1"
    asyncio.run(main(term, ver))
