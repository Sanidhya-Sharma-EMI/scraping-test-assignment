import asyncio
import json
import re
from pathlib import Path
from playwright.async_api import async_playwright

PROJECT = Path(__file__).resolve().parent.parent
URL_FILE = PROJECT / "exercise2" / "product_urls.json"
OUTPUT = PROJECT / "exercise2" / "product_page_details.json"
BACKUP = PROJECT / "exercise2" / "cellarbrations_results_backup.json"

DESCRIPTION_SELECTOR = (
    '[data-testid="pdpDangerouslySetDecription-span-testId"]'
)
MORE_SELECTOR = '[data-testid="viewMoreText-span-testId"]'

def extract_description(html):
    parts = []
    for chunk in re.split(r"<br\s*/?>", html, flags=re.I):
        from html import unescape
        import re as regex

        text = regex.sub(r"<[^>]+>", " ", unescape(chunk))
        text = " ".join(text.split())
        if text:
            parts.append(text)

    attr_index = next(
        (
            i for i, text in enumerate(parts)
            if re.match(
                r"^(Alcohol Volume|Pack Format|Standard Drinks|"
                r"Pack Type|Country of Origin):",
                text,
                re.I,
            )
        ),
        len(parts),
    )

    description = " ".join(parts[:attr_index])
    attributes = {}

    for text in parts[attr_index:]:
        if ":" in text:
            key, value = text.split(":", 1)
            attributes[key.strip()] = value.strip()

    return description, attributes

async def main():
    urls = json.loads(URL_FILE.read_text(encoding="utf-8"))

    # Preserve the records already collected manually.

    saved = {}
    for source in (BACKUP, OUTPUT):
        if source.exists():
            for record in json.loads(source.read_text(encoding="utf-8")):
                pid = str(record.get("product_id", ""))
                if pid:
                    saved[pid] = record

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(
            "http://localhost:9222"
        )
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()

        for number, url in enumerate(urls, start=1):
            match = re.search(r"id-(\d+)", url)
            product_id = match.group(1) if match else None

            if not product_id:
                print(f"[{number}/{len(urls)}] Skipped: no product ID")
                continue

            existing = saved.get(product_id)
            if existing and existing.get("description"):
                print(f"[{number}/{len(urls)}] Already collected: {product_id}")
                continue

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                await page.locator(DESCRIPTION_SELECTOR).first.wait_for(timeout=20000)

                more = page.locator(MORE_SELECTOR).first
                if await more.count() and "View Full" in (
                    await more.first.inner_text()
                ):
                    await more.first.click()
                    await page.wait_for_timeout(300)

                html = await page.locator(DESCRIPTION_SELECTOR).first.inner_html()
                description, attributes = extract_description(html)

                saved[product_id] = {
                    "product_id": product_id,
                    "product_url": page.url,
                    "description": description,
                    "attributes": attributes,
                }

                OUTPUT.write_text(
                    json.dumps(list(saved.values()), indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                print(f"[{number}/{len(urls)}] Saved {product_id}")

                # Be gentle with the website.
                await page.wait_for_timeout(1200)

            except Exception as exc:
                print(f"[{number}/{len(urls)}] Failed {product_id}: {exc}")

        await browser.close()

    print(f"Finished. {len(saved)} total product records in {OUTPUT}")

if __name__ == "__main__":
    asyncio.run(main())