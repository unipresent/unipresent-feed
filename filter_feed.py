import re
import requests
from html import unescape

URL = "https://www.unipresent.cz/google-merchant/1831"

r = requests.get(URL, timeout=300)
r.encoding = "utf-8"
feed = r.text

# Najdi všechny <item> bloky
items = re.findall(r"<item\b[\s\S]*?</item>", feed, flags=re.I)

cleaned_items = []

for item in items:
    # Jen produkty skladem
    if not re.search(r"<g:availability>\s*in\s*stock\s*</g:availability>", item, flags=re.I):
        continue

    # Odstranit zbytečné elementy (které nejsou pro AI důležité)
    remove_tags = [
        "g:custom_label_2", "g:custom_label_3", "g:custom_label_4",
        "g:custom_label_5", "g:adult", "g:shipping", "g:gtin",
        "g:brand", "g:condition"
    ]
    for tag in remove_tags:
        item = re.sub(rf"<{tag}[\s\S]*?</{tag}>", "", item, flags=re.I)

    # Odstranit HTML značky v popisu
    desc_match = re.search(r"<g:description>([\s\S]*?)</g:description>", item, flags=re.I)
    if desc_match:
        desc = unescape(desc_match.group(1))
        desc = re.sub(r"<.*?>", "", desc)  # odstraní HTML tagy, ale nechá text
        desc = re.sub(r"\s+", " ", desc).strip()
        item = re.sub(r"<g:description>[\s\S]*?</g:description>",
                      f"<g:description>{desc}</g:description>", item, flags=re.I)

    # Maximální komprese mezer a nových řádků
    item = re.sub(r">\s+<", "><", item)
    item = re.sub(r"\s+", " ", item)
    cleaned_items.append(item.strip())

# Vytvoř hlavičku a patičku XML
header = '<?xml version="1.0" encoding="utf-8"?><rss xmlns:g="http://base.google.com/ns/1.0" version="2.0"><channel>'
footer = "</channel></rss>"

xml_data = header + "".join(cleaned_items) + footer

# Uložit
with open("feed_instock.xml", "w", encoding="utf-8", newline="") as f:
    f.write(xml_data)

print("✅ Hotovo – feed_instock.xml zkomprimován beze ztrát.")
