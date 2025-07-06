#!/usr/bin/env python3
import warnings
from urllib3.exceptions import NotOpenSSLWarning, InsecureRequestWarning

# Suppress LibreSSL/OpenSSL warnings and insecure request warnings
warnings.filterwarnings('ignore', category=NotOpenSSLWarning)
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# HTTP headers to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept-Language': 'en-US'
}

# Hardcoded list of products with actual URLs
items = [
    {
        'Item': '12.75 oz Wine',
        'BrandURL': 'https://brandmybeverage.com/products/12-75-oz-wine-taster-glass',
        'DiscountMugsURL': 'https://www.discountmugs.com/product/7508-12oz-libbey-vina-wine-taster-glasses/',
        'EgrandstandURL': 'https://egrandstand.com/13-oz-libbey-vina-wine-taster-8552?queryID=d126ecbc24bf8029a3b55821002d902f&objectID=48880&indexName=gsg_default_products'
    },
    {
        'Item': '16 oz Can',
        'BrandURL': 'https://brandmybeverage.com/products/16-oz-can-glass',
        'DiscountMugsURL': 'https://www.discountmugs.com/product/e5458-16-oz-arc-plain-can-glass-tumblers/',
        'EgrandstandURL': 'https://egrandstand.com/16-oz-arc-can-glass-q5406?queryID=23cdbfbe801e8ef8addc189ffd14dcc3&objectID=97653&indexName=gsg_default_products'
    },
    {
        'Item': '12 OZ Alto',
        'BrandURL': 'https://brandmybeverage.com/products/12-oz-alto-goblet-wine-glass',
        'DiscountMugsURL': 'https://www.discountmugs.com/product/c8008-12-oz.-arc-connoisseur-custom-white-wine-glasses/',
        'EgrandstandURL': 'https://egrandstand.com/16-oz-arc-can-glass-q5406?queryID=23cdbfbe801e8ef8addc189ffd14dcc3&objectID=97653&indexName=gsg_default_products'
    },
    {
        'Item': '5.5 Oz Stemless',
        'BrandURL': 'https://brandmybeverage.com/products/5-5-oz-stemless-wine-taster-glass',
        'DiscountMugsURL': 'https://www.discountmugs.com/5-5-oz-arc-perfection-stemless-wine-glasses/',
        'EgrandstandURL': 'https://egrandstand.com/5-oz-arc-perfection-stemless-taster-d2015?queryID=2cdda0d51d0e091c9822033608cd2020&objectID=50344&indexName=gsg_default_products'
    },
    {
        'Item': '16oz Mixing',
        'BrandURL': 'https://brandmybeverage.com/products/16-oz-mixing-glass',
        'DiscountMugsURL': 'https://www.discountmugs.com/product/g3960-16oz-arc-pint-glasses/',
        'EgrandstandURL': 'https://egrandstand.com/16-oz-mixing-pint-glass?queryID=18bb6925d2310f8edcb2bedd9a7be958&objectID=128115&indexName=gsg_default_products'
    },
    {
        'Item': '16 oz. Belgian Tulip Beer',
        'BrandURL': 'https://brandmybeverage.com/products/16-oz-belgian-tulip-beer-glass',
        'DiscountMugsURL': 'https://www.discountmugs.com/product/3808-libbey-16-oz.-belgian-engraved-beer-glasses/',
        'EgrandstandURL': 'https://www.discountmugs.com/product/3808-libbey-16-oz.-belgian-engraved-beer-glasses/'
    },
    {
        'Item': '15 oz stemless wine glass',
        'BrandURL': 'https://brandmybeverage.com/products/15-oz-stemless-wine-glass',
        'DiscountMugsURL': 'https://www.discountmugs.com/product/c8303-15-oz-arc-stemless-etched-wine-glasses/',
        'EgrandstandURL': 'https://egrandstand.com/15-oz-arc-perfection-stemless-c8303?queryID=54e1a2d54b11beea24fb13b93cd926ed&objectID=49183&indexName=gsg_default_products'
    },
    {
        'Item': '8.5 oz Nuance Wine Glass',
        'BrandURL': 'https://brandmybeverage.com/products/8-5-oz-nuance-wine-glass',
        'DiscountMugsURL': 'https://www.discountmugs.com/product/5435al-8.5-oz.-aragon-custom-wine-glasses/',
        'EgrandstandURL': 'https://egrandstand.com/8-oz-libbey-citation-wine-8464?queryID=bb8af8146c95649d5e4e06294703e116&objectID=48873&indexName=gsg_default_products'
    },
    {
        'Item': '5.75 oz Arc Nuance',
        'BrandURL': 'https://brandmybeverage.com/products/5-75-oz-nuance-flute',
        'DiscountMugsURL': 'https://www.discountmugs.com/product/09192-5.75-oz.-arc-nuance-custom-champagne-flutes/',
        'EgrandstandURL': 'https://egrandstand.com/6-oz-libbey-napa-country-flute-8795?queryID=13cdf1c7460c4b7dd911e2741ac10178&objectID=48885&indexName=gsg_default_products'
    }
]

def fetch_price(url, regex=None, selectors=None):
    """
    Fetch a URL and extract a price.
    - If `selectors` is provided, look inside those CSS selectors first.
    - Otherwise fall back to regex search over the entire page text.
    - If the regex contains a capturing group, return group(1).
    """
    try:
        resp = requests.get(url, headers=headers, timeout=10, verify=False)
        resp.raise_for_status()
    except requests.exceptions.RequestException:
        return None

    soup = BeautifulSoup(resp.text, 'html.parser')

    # 1) Try selectors
    if selectors:
        for sel in selectors:
            el = soup.select_one(sel)
            if el and '$' in el.get_text():
                m = re.search(r"\$[0-9,]+\.\d{2}", el.get_text())
                if m:
                    return m.group()

    # 2) Fallback to regex over full text
    text = soup.get_text(separator=' ')
    pattern = regex or r"\$[0-9,]+\.\d{2}"
    m = re.search(pattern, text)
    if not m:
        return None
    # If capturing group exists, return that
    if m.lastindex:
        return m.group(1)
    return m.group()


def main():
    rows = []
    for item in items:
        rows.append({
            'Item': item['Item'],
            'Brand My Beverage': fetch_price(
                item['BrandURL'],
                selectors=['span.money','span.price','.product-price','.price-item']
            ),
            'Discount Mugs': fetch_price(
                item['DiscountMugsURL'],
                regex=r"5000\+[^\$]*(\$[0-9,]+\.\d{2})"
            ),
            'Egrandstand': fetch_price(
                item['EgrandstandURL'],
                selectors=['.product-price','.price','span.price']
            )
        })

    df = pd.DataFrame(rows)
    print(df.to_string(index=False))
    df.to_excel('prices.xlsx', index=False)


if __name__ == '__main__':
    main()
