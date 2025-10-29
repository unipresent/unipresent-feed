import re
import requests

URL = "https://www.unipresent.cz/google-merchant/1831"

r = requests.get(URL, timeout=300)
r.encoding = "utf-8"
feed = r.text

# Najdi všechny <item> bloky
items = re.findall(r"<item[\s\S]*?</item>", feed)

cleaned_items = []
for item in items:
    # pouze produkty skladem
    if not re.search(r"<g:availability>\s*in stock\s*</g:availability>", item, re.I):
        continue

    # Odstraň všechny nepotřebné části
    item = re.sub(r"<g:custom_label_0>[\s\S]*?</g:custom_label_0>", "", item, flags=re.I)
    item = re.sub(r"<g:custom_label_1>[\s\S]*?</g:custom_label_1>", "", item, flags=re.I)
    item = re.sub(r"<g:condition>[\s\S]*?</g:condition>", "", item, flags=re.I)
    item = re.sub(r"<g:adult>[\s\S]*?</g:adult>", "", item, flags=re.I)
    item = re.sub(r"<g:shipping>[\s\S]*?</g:shipping>", "", item, flags=re.I)
    item = re.sub(r"<g:gtin>[\s\S]*?</g:gtin>", "", item, flags=re.I)
    item = re.sub(r"<g:brand>[\s\S]*?</g:brand>", "", item, flags=re.I)

    # Odstraň vícenásobné prázdné řádky / mezery
    item = re.sub(r"\n\s*\n", "\n", item.strip())

    cleaned_items.append(item)

# Hlavička a patička XML
header_match = re.search(r"^.*?<channel>", feed, re.S)
footer_match = re.search(r"</channel>\s*</rss>\s*$", feed, re.S)

header = header_match.group(0) if header_match else '<?xml version="1.0" encoding="utf-8"?><rss xmlns:g="http://base.google.com/ns/1.0" version="2.0"><channel>'
footer = footer_match.group(0) if footer_match else "</channel></rss>"

# Výsledné XML
xml_data = header + "\n" + "\n".join(cleaned_items) + "\n" + footer

# Ulož jako UTF-8 (bez prázdných řádků)
with open("feed_instock.xml", "w", encoding="utf-8", newline="") as f:
    f.write(xml_data.strip() + "\n")
