import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep
from tqdm import tqdm
import xml.etree.ElementTree as ET
import json

# Configuraciones generales
SITEMAP_URL = "https://developer.signalwire.com/freeswitch/sitemap.xml"
MAX_WORKERS = 10
WAIT_BETWEEN = 0.1
MAX_TEXT_LENGTH = 100_000
TARGET_DIV_CLASS = "theme-doc-markdown markdown"


def get_urls_from_sitemap(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)

        # namespaces para manejar xmlns
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        urls = []
        for url_tag in root.findall('ns:url', ns):
            loc = url_tag.find('ns:loc', ns)
            if loc is not None:
                urls.append(loc.text.strip())
        return urls

    except Exception as e:
        print(f"❌ Error al obtener sitemap: {e}")
        return []


def clean_html_target_div(html):
    soup = BeautifulSoup(html, "html.parser")

    # Buscar solo el div de contenido principal
    main_content = soup.find("div", class_=TARGET_DIV_CLASS)
    if not main_content:
        return ""

    for tag in main_content(["script", "style", "noscript"]):
        tag.decompose()

    return main_content.get_text(separator=" ", strip=True)


def scrape(url):
    try:
        resp = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (compatible; ScraperBot/1.0)"
        })
        resp.raise_for_status()
        text = clean_html_target_div(resp.text)

        return {
            "url": url,
            "text": text[:MAX_TEXT_LENGTH] if text else "(No se encontró el contenido objetivo)"
        }

    except Exception as e:
        return {
            "url": url,
            "error": str(e)
        }


def main():
    print(f"🔍 Descargando sitemap desde: {SITEMAP_URL}")
    urls = get_urls_from_sitemap(SITEMAP_URL)
    print(f"✅ {len(urls)} URLs encontradas")

    if not urls:
        print("⚠️ No se encontraron URLs, abortando.")
        return

    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(scrape, url): url for url in urls}
        for future in tqdm(as_completed(futures), total=len(urls)):
            results.append(future.result())
            sleep(WAIT_BETWEEN)

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("📄 Scraping completado. Guardado en output.json")


if __name__ == "__main__":
    main()
