import re
import requests

# Zdrojový feed
URL = "https://www.unipresent.cz/google-merchant/1831"

r = requests.get(URL, timeout=300)
r.encoding = "utf-8"
feed = r.text

# Najdi všechny bloky <item>...</item>
items = re.findall(r"<item\b[\s\S]*?</item>", feed, flags=re.I)

cleaned_items = []

for item in items:
    # Jen produkty skladem
    if not re.search(r"<\s*g:availability\s*>\s*in\s*stock\s*<\s*/\s*g:availability\s*>", item, flags=re.I):
        continue

    # Odstranit nepotřebné části
    item = re.sub(r"<\s*g:id\s*>[\s\S]*?<\s*/\s*g:id\s*>", "", item, flags=re.I)
    item = re.sub(r"<\s*g:custom_label_0\s*>[\s\S]*?<\s*/\s*g:custom_label_0\s*>", "", item, flags=re.I)
    item = re.sub(r"<\s*g:custom_label_[2-9]\s*>[\s\S]*?<\s*/\s*g:custom_label_[2-9]\s*>", "", item, flags=re.I)
    item = re.sub(r"<\s*g:condition\s*>[\s\S]*?<\s*/\s*g:condition\s*>", "", item, flags=re.I)
    item = re.sub(r"<\s*g:adult\s*>[\s\S]*?<\s*/\s*g:adult\s*>", "", item, flags=re.I)
    item = re.sub(r"<\s*g:shipping\b[\s\S]*?<\s*/\s*g:shipping\s*>", "", item, flags=re.I)
    item = re.sub(r"<\s*g:gtin\s*>[\s\S]*?<\s*/\s*g:gtin\s*>", "", item, flags=re.I)
    item = re.sub(r"<\s*g:brand\s*>[\s\S]*?<\s*/\s*g:brand\s*>", "", item, flags=re.I)
    item = re.sub(r"<\s*g:image_link\s*>[\s\S]*?<\s*/\s*g:image_link\s*>", "", item, flags=re.I)

    # Vyčistit HTML entity uvnitř <g:description>
    # 1️⃣ odstranit všechny značky typu &lt;p&gt;, &lt;li&gt;, &lt;b&gt; atd.
    item = re.sub(r"&lt;/?[a-zA-Z0-9]+.*?&gt;", "", item)
    # 2️⃣ převod běžných HTML entit
    item = re.sub(r"&amp;", "&", item)
    item = re.sub(r"&quot;", '"', item)
    item = re.sub(r"&apos;", "'", item)
    item = re.sub(r"&nbsp;", " ", item)
    item = re.sub(r"&lt;", "<", item)
    item = re.sub(r"&gt;", ">", item)
    # 3️⃣ odstranit vícenásobné mezery
    item = re.sub(r"\s{2,}", " ", item)

    # Odstranit zbytečné mezery mezi značkami
    item = re.sub(r">\s+<", "><", item)
    # Odstranit vícenásobné nové řádky
    item = re.sub(r"\n+", "\n", item.strip())

    cleaned_items.append(item.strip())

# Najdi hlavičku a patičku
header_match = re.search(r"^.*?<channel\s*>", feed, flags=re.S | re.I)
footer_match = re.search(r"</channel\s*>\s*</rss\s*>\s*$", feed, flags=re.S | re.I)

header = header_match.group(0) if header_match else '<?xml version="1.0" encoding="utf-8"?><rss xmlns:g="http://base.google.com/ns/1.0" version="2.0"><channel>'
footer = footer_match.group(0) if footer_match else "</channel></rss>"

# Složit výsledek
xml_data = header.strip() + "\n" + "\n".join(cleaned_items) + "\n" + footer.strip()

# Finální čištění
xml_data = re.sub(r"\n{2,}", "\n", xml_data)

# Uložit výsledek
with open("feed_instock.xml", "w", encoding="utf-8", newline="") as f:
    f.write(xml_data + "\n")

print("✅ Hotovo – feed_instock.xml byl vygenerován.")
