import re
import requests

URL = "https://www.unipresent.cz/google-merchant/1831"

# stáhni celý XML feed
r = requests.get(URL, timeout=300)
r.encoding = "utf-8"
feed = r.text

# vyber pouze <item> s dostupností in stock
items = re.findall(r"<item[\s\S]*?</item>", feed)
instock = [x for x in items if "<g:availability>in stock</g:availability>" in x.lower()]

header = feed.split("<item>")[0]
footer = "</channel></rss>"

# slož výsledek
xml_data = header + "".join(instock) + footer

# uložit přesně tak, jak je (žádná konverze)
with open("feed_instock.xml", "w", encoding="utf-8", newline="") as f:
    f.write(xml_data)
