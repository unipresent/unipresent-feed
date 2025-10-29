import re
import requests

URL = "https://www.unipresent.cz/google-merchant/1831"

# stáhni celý XML feed
r = requests.get(URL, timeout=300)
r.encoding = "utf-8"
feed = r.text

# vyber všechny položky <item>...</item>
items = re.findall(r"<item[\s\S]*?</item>", feed)

cleaned_items = []
for item in items:
    # bereme jen produkty skladem
    if "<g:availability>in stock</g:availability>" not in item.lower():
        continue

    # odstranění nepotřebných tagů
    item = re.sub(r"<g:custom_label_0>.*?</g:custom_label_0>", "", item, flags=re.S)
    item = re.sub(r"<g:custom_label_1>.*?</g:custom_label_1>", "", item, flags=re.S)
    item = re.sub(r"<g:condition>.*?</g:condition>", "", item, flags=re.S)
    item = re.sub(r"<g:adult>.*?</g:adult>", "", item, flags=re.S)
    item = re.sub(r"<g:shipping>.*?</g:shipping>", "", item, flags=re.S)

    cleaned_items.append(item.strip())

# hlavička a patička XML
header_match = re.search(r"^.*?<channel>", feed, re.S)
footer_match = re.search(r"</channel>\s*</rss>\s*$", feed, re.S)

header = header_match.group(0) if header_match else '<?xml version="1.0" encoding="utf-8"?><rss xmlns:g="http://base.google.com/ns/1.0" version="2.0"><channel>'
footer = footer_match.group(0) if footer_match else "</channel></rss>"

# složení výsledku
xml_data = header + "\n" + "\n".join(cleaned_items) + "\n" + footer

# zápis do souboru
with open("feed_instock.xml", "w", encoding="utf-8", newline="") as f:
    f.write(xml_data)
