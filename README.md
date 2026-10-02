# Web Scraping Assignment

This repository contains two web-scraping exercises: Glossier product data and Cellarbrations whisky product data.

## Project Structure

```text
scraping_test_assignment/
├── exercise1/
│   └── scraper.py
├── exercise2/
│   ├── automate_descriptions.py
│   ├── build_csv.py
│   ├── page1_products.json
│   ├── page2_products.json
│   ├── product_urls.json
│   └── product_page_details.json
├── output/
│   ├── glossier_products_in.csv
│   ├── glossier_products_us.csv
│   └── cellarbrations_whisky.csv
├── requirements.txt
├── notes.txt
├── README.md
└── .gitignore
```

## Requirements

* Python 3.10 or later
* pip
* Microsoft Edge for the connected-browser product-description workflow in Exercise 2

## Setup

Clone the repository and navigate to its root directory.

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Exercise 1 — Glossier

The scraper collects product and variant information for the India and US markets.

In `exercise1/scraper.py`, select the market by setting:

```python
MARKET = "in"
```

Use `"us"` for the United States market.

Run:

```powershell
python exercise1/scraper.py
```

The generated CSV is saved in the `output/` directory.

Existing output files:

* `output/glossier_products_in.csv`
* `output/glossier_products_us.csv`

## Exercise 2 — Cellarbrations Whisky

The dataset contains 57 unique products collected from two category pages.

The category listing data is stored in:

* `exercise2/page1_products.json`
* `exercise2/page2_products.json`

### Generate the CSV

Run:

```powershell
python exercise2/scraper.py
```

The script combines the category records with product-page descriptions, extracts measuring units and quantities from product names, removes duplicate product IDs, and writes:

`output/cellarbrations_whisky.csv`

### Product-page descriptions

The script `exercise2/automate_descriptions.py` collects product descriptions using a connected Microsoft Edge session through CDP.

The browser must be launched with remote debugging enabled on port `9222`, and the website must be accessible in that session. The script reads `exercise2/product_urls.json` and saves its results to `exercise2/product_page_details.json`.

The category listing exports are provided as saved JSON files; the entire category collection process is not currently unattended.

## Validation

The current output files contain:

| Dataset               | Rows | Duplicate product IDs |
| --------------------- | ---: | --------------------: |
| Glossier India        |  321 |                     0 |
| Glossier US           |  353 |                     0 |
| Cellarbrations Whisky |   57 |                     0 |

Some Glossier products have missing descriptions because no description was available from the sources checked. See `notes.txt` for validation details, collection limitations, the HTTP-versus-browser comparison, and AI assistance disclosure.

## Notes

Read `notes.txt` for further details about the collection methodology, data validation, limitations, and the use of AI assistance.
