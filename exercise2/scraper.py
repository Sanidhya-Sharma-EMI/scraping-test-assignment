
import json
import re
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

INPUT_FILES = [
    BASE_DIR / "page1_products.json",
    BASE_DIR / "page2_products.json",
]

DETAILS_FILE = BASE_DIR / "product_page_details.json"

COLUMNS = [
    "name",
    "product_id",
    "product_url",
    "image_url",
    "price",
    "scraped_at",
    "description",
    "measuring_units",
    "units",
]


def parse_pack_size(name):
    match = re.search(r"\b(\d+(?:\.\d+)?)\s*(mL|ml|ML|L|l)\b", name)
    if not match:
        return None, None

    units = float(match.group(1))
    measuring_units = match.group(2)

    if units.is_integer():
        units = int(units)

    return measuring_units, units


def main():
    products = []

    for file_path in INPUT_FILES:
        with file_path.open("r", encoding="utf-8") as file:
            products.extend(json.load(file))

    # Load full descriptions collected from product detail pages.
    with DETAILS_FILE.open("r", encoding="utf-8") as file:
        details = json.load(file)

    descriptions_by_id = {
        str(item["product_id"]): item.get("description", "")
        for item in details
        if item.get("product_id") is not None
    }

    for product in products:
        product_id = str(product.get("product_id", ""))
        full_description = descriptions_by_id.get(product_id, "")

        if full_description:
            product["description"] = full_description

        product["measuring_units"], product["units"] = parse_pack_size(
            product.get("name", "")
        )

    df = pd.DataFrame(products)

    for column in COLUMNS:
        if column not in df.columns:
            df[column] = None

    df = df[COLUMNS]
    df = df.drop_duplicates(subset=["product_id"])

    output_file = OUTPUT_DIR / "cellarbrations_whisky.csv"
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"CSV saved: {output_file}")
    print(f"Products exported: {len(df)}")
    print(f"Duplicate product IDs: {df['product_id'].duplicated().sum()}")
    print(f"Missing descriptions: {df['description'].isna().sum()}")
    print(f"Empty descriptions: {(df['description'].fillna('').str.strip() == '').sum()}")
    print(f"Missing image URLs: {df['image_url'].isna().sum()}")
    print(f"Missing prices: {df['price'].isna().sum()}")


if __name__ == "__main__":
    main()