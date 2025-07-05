from playwright.async_api import async_playwright
from config import NVD_URL


async def search_with_playwright(queries, str_url=NVD_URL):
    """Usa Playwright per cercare vulnerabilità su web (esempio su NVD)."""
    alerts = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        for qry in queries:
            await page.goto(str_url)
            await page.fill('#keyword', qry)
            await page.click('button[type="submit"]')
            await page.wait_for_selector('.vuln-title')
            titles = await page.eval_on_selector_all('.vuln-title', 'els => els.map(e=>e.innerText)')
            for t in titles:
                alerts.append(f"{qry}: {t}")
        await browser.close()
    return alerts

