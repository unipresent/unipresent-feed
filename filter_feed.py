import re
import requests

URL = "https://www.unipresent.cz/google-merchant/1831"
response = requests.get(URL, timeout=180)
response.encoding = "utf-8"
feed = response.text

# Získej všechny položky
items = re.findall(r"<item[\s\S]*?</item>", feed)

# Vyfiltruj pouze 'in stock'
in_stock = [i for i in items if re.search(r"<g:availability>\s*in stock\s*</g:availability>", i, re.I)]

# Najdi hlavičku a patičku XML
header_match = re.search(r"^.*?<channel>", feed, re.S)
footer_match = re.search(r"</channel>\s*</rss>\s*$", feed, re.S)

header = header_match.group(0) if header_match else '<?xml version="1.0" encoding="utf-8"?><rss xmlns:g="http://base.google.com/ns/1.0" version="2.0"><channel>'
footer = footer_match.group(0) if footer_match else "</channel></rss>"

# Slož finální XML strukturu
filtered_feed = f"{header}\n" + "\n".join(in_stock) + f"\n{footer}"

# Ulož jako UTF-8 XML
with open("feed_instock.xml", "w", encoding="utf-8") as f:
    f.write(filtered_feed)
