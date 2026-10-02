
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.glossier.com"
MARKET = "us"  # Use "in" for India or "us" for the United States

COLLECTION_PATH = (
    "/en-in/collections/all" if MARKET == "in"
    else "/collections/all"
)

PRODUCTS_URL = (
    f"{BASE_URL}{COLLECTION_PATH}/products.json?limit=250"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_product_description(product):
    """Get a product description from JSON, page HTML, or JSON-LD metadata."""
    description = BeautifulSoup(
        product.get("body_html", ""),
        "html.parser"
    ).get_text(" ", strip=True)

    if description:
        return description

    locale_prefix = "/en-in" if MARKET == "in" else ""
    product_url = f"{BASE_URL}{locale_prefix}/products/{product['handle']}"

    response = requests.get(
        product_url,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # First fallback: visible product description.
    description_element = soup.select_one("#description-item")

    if description_element:
        description = description_element.get_text(" ", strip=True)

    # Second fallback: structured JSON-LD product metadata.
    if not description:
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                data = json.loads(script.string or script.get_text())
            except (json.JSONDecodeError, TypeError):
                continue

            items = data if isinstance(data, list) else [data]

            for item in items:
                if not isinstance(item, dict):
                    continue

                if item.get("@type") == "Product" and item.get("description"):
                    description = BeautifulSoup(
                        item["description"],
                        "html.parser"
                    ).get_text(" ", strip=True)
                    break

            if description:
                break

    return description


def scrape_products():
    """Fetch products and create one row per product variant."""
    response = requests.get(
        PRODUCTS_URL,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()

    products = response.json()["products"]
    rows = []

    for product in products:
        description = get_product_description(product)

        for variant in product.get("variants", []):
            variant_id = variant["id"]

            # Prefer the variant image; otherwise use the first product image.
            image = None

            if variant.get("featured_image"):
                image = variant["featured_image"].get("src")
            elif product.get("images"):
                image = product["images"][0].get("src")


            product_url = (
                f"{BASE_URL}"
                f"{'/en-in' if MARKET == 'in' else ''}"
                f"/products/{product['handle']}?variant={variant_id}"
            )

            rows.append({
                "product_name": product["title"],
                "product_id": variant_id,
                "product_url": product_url,
                "image": image,
                "price": variant["price"],
                "description": description,
                "variant": variant["title"],
                "scraped_at": datetime.now(timezone.utc).isoformat()
            })

    return len(products), rows


def main():
    product_count, rows = scrape_products()

    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"glossier_products_{MARKET}.csv"
    df = pd.DataFrame(rows)
    df.to_csv(output_file, index=False)

    print(f"Products found: {product_count}")
    print(f"Variants found: {len(rows)}")
    print(f"Saved to {output_file}")
    print(f"Missing descriptions: {df['description'].isna().sum() + (df['description'].fillna('').str.strip() == '').sum()}")


if __name__ == "__main__":
    main()
