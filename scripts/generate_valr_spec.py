#!/usr/bin/env python3
"""
Scrape public VALR documentation and draft an OpenAPI 3.0 spec automatically
using a local LLM (Ollama).
"""

from bs4 import BeautifulSoup
import requests
from langchain.prompts import PromptTemplate
from langchain.llms import Ollama
from pathlib import Path
import re
import yaml


BASE_URL = "https://docs.valr.com/"
OUT_PATH = Path("openapi/generated/valr_paths.yaml")
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Initialise local model
llm = Ollama(model="llama3", temperature=0)

prompt_tmpl = PromptTemplate.from_template(
    """
You are an API expert creating OpenAPI 3 path stubs.
From the text below, produce a valid YAML block for the `paths:` section only.
Keep it concise and syntactically valid.

Text:
{endpoint_text}

Return YAML only.
"""
)


def scrape_docs(base_url):
    """Grab all subpages under docs.valr.com"""
    html = requests.get(base_url).text
    soup = BeautifulSoup(html, "html.parser")

    # Find doc links (anchor tags within navigation)
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("https://docs.valr.com") and href not in links:
            links.append(href)
    return links


def extract_endpoints(page_html):
    """Parse endpoints and their surrounding description blocks"""
    soup = BeautifulSoup(page_html, "html.parser")
    text = soup.get_text()
    blocks = re.findall(r"(GET|POST|PUT|DELETE)\s+/v\d+/.+?(?=\n[A-Z]{3,5}\s+/|$)", text, re.DOTALL)
    return [b.strip() for b in blocks]


def llm_to_yaml(text_block):
    """Ask model to convert to OpenAPI YAML block"""
    try:
        return llm(prompt_tmpl.format(endpoint_text=text_block)).strip()
    except Exception as e:
        print("LLM failed:", e)
        return None


def main():
    all_snippets = []
    for link in scrape_docs(BASE_URL):
        print(f"🧭 Scanning {link}")
        page_html = requests.get(link).text
        endpoints = extract_endpoints(page_html)
        for ep_text in endpoints:
            print(f"→ Generating spec for {ep_text.split()[1][:40]}...")
            yaml_fragment = llm_to_yaml(ep_text)
            if yaml_fragment:
                all_snippets.append(yaml_fragment)

    # Write aggregated file
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("paths:\n")
        for block in all_snippets:
            # Indent correctly under paths:
            indented = "\n".join("  " + line for line in block.splitlines())
            f.write(indented + "\n")

    print(f"\n✅ Draft written to {OUT_PATH} — validate with:\n"
          f"   openapi validate {OUT_PATH}")


if __name__ == "__main__":
    main()
    