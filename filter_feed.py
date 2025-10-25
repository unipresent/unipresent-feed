import re
import requests

URL = "https://www.unipresent.cz/google-merchant/1831"

# Stáhni XML jako čistý text
response = requests.get(URL, timeout=300)
response.encoding = "utf-8"
feed = response.text

# Najdi všechny bloky <item>...</item>
items = re.findall(r"<item[\s\S]*?</item>", feed)

# Vyfiltruj pouze ty, které jsou 'in stock'
in_stock = [
    i for i in items
    if re.search(r"<g:availability>\s*in stock\s*</g:availability>", i, re.I)
]

# Najdi hlavičku a patičku (včetně XML deklarace)
header_match = re.search(r"^.*?<channel>", feed, re.S)
footer_match = re.search(r"</channel>\s*</rss>\s*$", feed, re.S)

header = header_match.group(0) if header_match else '<?xml version="1.0" encoding="utf-8"?><rss xmlns:g="http://base.google.com/ns/1.0" version="2.0"><channel>'
footer = footer_match.group(0) if footer_match else "</channel></rss>"

# Slož nové XML (doslova)
filtered_feed = header + "\n" + "\n".join(in_stock) + "\n" + footer

# Ulož jako UTF-8, bez převodu tagů
with open("feed_instock.xml", "wb") as f:
    f.write(filtered_feed.encode("utf-8"))
