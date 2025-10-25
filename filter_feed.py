import re, requests

URL = "https://www.unipresent.cz/google-merchant/1831"
feed = requests.get(URL, timeout=120).text

items = re.findall(r"<item[\s\S]*?</item>", feed)
in_stock = [i for i in items if re.search(r"<g:availability>\s*in stock\s*</g:availability>", i, re.I)]

header = feed.split("<item>")[0]
footer = "</channel></rss>"
filtered = header + "\n".join(in_stock) + footer

with open("feed_instock.xml", "w", encoding="utf-8") as f:
    f.write(filtered)
