import re
import requests

URL = "https://www.unipresent.cz/google-merchant/1831"

r = requests.get(URL, timeout=300)
r.encoding = "utf-8"
feed = r.text

# Najdi všechny <item> bloky (robustně)
items = re.findall(r"<item\b[\s\S]*?</item>", feed, flags=re.I)

cleaned_items = []
for item in items:
    # jen produkty skladem (case-insensitive, tolerantní na mezery)
    if not re.search(r"<\s*g:availability\s*>\s*in\s+stock\s*<\s*/\s*g:availability\s*>", item, flags=re.I):
        continue

    # SMAZAT:
    # - g:id
    item = re.sub(r"<\s*g:id\s*>[\s\S]*?<\s*/\s*g:id\s*>", "", item, flags=re.I)
    # - g:custom_label_0 (POZOR: custom_label_1 necháváme!)
    item = re.sub(r"<\s*g:custom_label_0\s*>[\s\S]*?<\s*/\s*g:custom_label_0\s*>", "", item, flags=re.I)
    # - g:condition
    item = re.sub(r"<\s*g:condition\s*>[\s\S]*?<\s*/\s*g:condition\s*>", "", item, flags=re.I)
    # - g:adult
    item = re.sub(r"<\s*g:adult\s*>[\s\S]*?<\s*/\s*g:adult\s*>", "", item, flags=re.I)
    # - celý blok g:shipping (s vnořenými tagy)
    item = re.sub(r"<\s*g:shipping\b[\s\S]*?<\s*/\s*g:shipping\s*>", "", item, flags=re.I)
    # - g:gtin
    item = re.sub(r"<\s*g:gtin\s*>[\s\S]*?<\s*/\s*g:gtin\s*>", "", item, flags=re.I)
    # - g:brand
    item = re.sub(r"<\s*g:brand\s*>[\s\S]*?<\s*/\s*g:brand\s*>", "", item, flags=re.I)

    # ZKOMPRESOVAT prázdné řádky / nadbytečné mezery mezi tagy
    item = re.sub(r"\n[ \t]*\n+", "\n", item.strip())

    cleaned_items.append(item)

# Hlavička a patička XML
header_match = re.search(r"^.*?<channel\s*>", feed, flags=re.S|re.I)
footer_match = re.search(r"</channel\s*>\s*</rss\s*>\s*$", feed, flags=re.S|re.I)

header = header_match.group(0) if header_match else '<?xml version="1.0" encoding="utf-8"?><rss xmlns:g="http://base.google.com/ns/1.0" version="2.0"><channel>'
footer = footer_match.group(0) if footer_match else "</channel></rss>"

# Výsledné XML
xml_data = header + "\n" + "\n".join(cleaned_items) + "\n" + footer
xml_data = re.sub(r"\n[ \t]*\n+", "\n", xml_data.strip()) + "\n"

# Zápis (UTF-8, beze změny tagů)
with open("feed_instock.xml", "w", encoding="utf-8", newline="") as f:
    f.write(xml_data)
