import pandas as pd
from pathlib import Path

output_dir = Path("output")

files = [
    "glossier_products_in.csv",
    "glossier_products_us.csv",
    "cellarbrations_whisky.csv",
]

for filename in files:
    path = output_dir / filename

    if not path.exists():
        print(f"\n--- {filename} ---")
        print("ERROR: File not found")
        continue

    df = pd.read_csv(path)

    print(f"\n--- {path.name} ---")
    print("Rows:", len(df))

    if "product_id" in df.columns:
        print("Duplicate product IDs:", df["product_id"].duplicated().sum())

    for column in [
        "product_name",
        "product_url",
        "image",
        "price",
        "description",
        "variant",
    ]:
        if column in df.columns:
            print(f"Missing {column}:", df[column].isna().sum())
