import requests
import trafilatura

url = "https://en.wikipedia.org/wiki/Mohamed_Bachir_El_Ibrahimi"
html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
text = trafilatura.extract(html)
print(f"Length: {len(text)} chars")
print(text[:500])