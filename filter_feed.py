import re
import requests
import os
from html import unescape

URL = "https://www.unipresent.cz/google-merchant/1831"

r = requests.get(URL, timeout=300)
r.encoding = "utf-8"
feed = r.text

items = re.findall(r"<item\b[\s\S]*?</item>", feed, flags=re.I)
cleaned_items = []

for item in items:
    # Jen produkty skladem
    if not re.search(r"<\s*g:availability\s*>\s*in\s*stock\s*<\s*/\s*g:availability\s*>", item, flags=re.I):
        continue

    # Najdi description
    desc_match = re.search(r"<g:description>([\s\S]*?)</g:description>", item, flags=re.I)
    if not desc_match:
        continue  # ⚠️ přeskočit produkty bez <g:description>

    desc = desc_match.group(1).strip()
    if not desc:
        continue  # ⚠️ přeskočit produkty s prázdným popisem

    # 🧹 Odstranit nepotřebné tagy
    item = re.sub(r"<\s*g:id\s*>[\s\S]*?<\s*/\s*g:id\s*>", "", item, flags=re.I)
    item = re.sub(r"<\s*g:custom_label_[0-9]\s*>[\s\S]*?<\s*/\s*g:custom_label_[0-9]\s*>", "", item, flags=re.I)
    item = re.sub(r"<\s*g:condition\s*>[\s\S]*?<\s*/\s*g:condition\s*>", "", item, flags=re.I)
    item = re.sub(r"<\s*g:adult\s*>[\s\S]*?<\s*/\s*g:adult\s*>", "", item, flags=re.I)
    item = re.sub(r"<\s*g:shipping\b[\s\S]*?<\s*/\s*g:shipping\s*>", "", item, flags=re.I)
    item = re.sub(r"<\s*g:gtin\s*>[\s\S]*?<\s*/\s*g:gtin\s*>", "", item, flags=re.I)
    item = re.sub(r"<\s*g:brand\s*>[\s\S]*?<\s*/\s*g:brand\s*>", "", item, flags=re.I)
    item = re.sub(r"<\s*g:image_link\s*>[\s\S]*?<\s*/\s*g:image_link\s*>", "", item, flags=re.I)

    # ✨ Vyčistit description – HTML značky pryč, text zůstává
    desc = unescape(desc)
    desc = re.sub(r"<[^>]+>", " ", desc)
    desc = re.sub(r"\s{2,}", " ", desc).strip()

    # ✏️ Vložit zpět vyčištěný popis (bez zkrácení!)
    item = re.sub(r"<g:description>[\s\S]*?</g:description>",
                  f"<g:description>{desc}</g:description>", item, flags=re.I)

    # 🧩 Vyčistit mezery mezi značkami
    item = re.sub(r">\s+<", "><", item)
    item = re.sub(r"\n+", "", item.strip())

    cleaned_items.append(item.strip())

# 🔖 Hlavička a patička
header_match = re.search(r"^.*?<channel\s*>", feed, flags=re.S | re.I)
footer_match = re.search(r"</channel\s*>\s*</rss\s*>\s*$", feed, flags=re.S | re.I)
header = header_match.group(0) if header_match else '<?xml version="1.0" encoding="utf-8"?><rss xmlns:g="http://base.google.com/ns/1.0" version="2.0"><channel>'
footer = footer_match.group(0) if footer_match else "</channel></rss>"

# 📦 Složit výsledek
xml_data = header.strip() + "".join(cleaned_items) + footer.strip()

# 💾 Uložit
with open("feed_instock.xml", "w", encoding="utf-8", newline="") as f:
    f.write(xml_data)

# 📏 Výpis velikosti a počtu produktů
size_mb = os.path.getsize("feed_instock.xml") / (1024 * 1024)
print(f"✅ Hotovo – feed_instock.xml ({size_mb:.2f} MB, {len(cleaned_items)} produktů)")
