import asyncio
from playwright.async_api import async_playwright

def versione_in_range(versione_target, versioni_vulnerabili):
    # verifica semplificata di inclusione
    return any(versione_target == v for v in versioni_vulnerabili)

async def main(search_term, versione_target):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Vai alla ricerca NVD
        search_url = f"https://nvd.nist.gov/vuln/search/results?query={search_term}&search_type=all"
        await page.goto(search_url)

        # Attendi la tabella dei risultati usando data-testid
        await page.wait_for_selector('table[data-testid="vuln-results-table"]', timeout=60000)

        # Estrai i link alle pagine dettaglio CVE
        links = await page.eval_on_selector_all(
            'table[data-testid="vuln-results-table"] tbody tr th a',
            'els => els.map(e => e.href)'
        )
        print(f"Trovate {len(links)} CVE per '{search_term}'")

        for link in links:
            print(f"\n— Controllo {link}")
            await page.goto(link)
            await page.wait_for_selector('section#vuln-software-configuration', timeout=30000)

            # Estrai il testo delle configurazioni software
            cpe_text = await page.eval_on_selector(
                'section#vuln-software-configuration',
                'el => el.innerText'
            )

            # Cerca le versioni vulnerabili relative al search_term
            versioni_vulnerabili = []
            for line in cpe_text.splitlines():
                if search_term.lower() in line.lower():
                    parts = line.split(':')
                    if len(parts) > 4:
                        versioni_vulnerabili.append(parts[4])

            if versione_in_range(versione_target, versioni_vulnerabili):
                print(f"⚠️ La versione {versione_target} RISULTA vulnerabile")
            else:
                print(f"✅ La versione {versione_target} NON risulta vulnerabile")

        await browser.close()

if __name__ == "__main__":
    import sys
    term = sys.argv[1] if len(sys.argv) > 1 else "neo4j"
    ver  = sys.argv[2] if len(sys.argv) > 2 else "3.5.0"
    asyncio.run(main(term, ver))
