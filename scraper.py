"""
Scrapes country profiles at https://www.policinglaw.info/ to pdf.
"""

import os
import tempfile
import subprocess
from typing import List
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify
from alive_progress import alive_it

BASE_URL = "https://www.policinglaw.info/"


def collect_country_urls(url: str) -> List[str]:
    """Collects all country URLs."""
    req = requests.get(url=url)
    soup = BeautifulSoup(req.content, "html.parser")
    urls = []
    dropdown = soup.find("ul", class_="dropdown-menu country-dropdown")
    for li in dropdown.find_all("li"):
        urls.append(li.a.get("href"))
    return urls


def compile_pdfs(country_urls: List[str], path: str) -> None:
    """Compiles page to markdown and pdf."""
    for url in alive_it(country_urls):
        name = url.split("/")[-2]
        req = requests.get(url=url)
        soup = BeautifulSoup(req.content, "html.parser")
        header = soup.find("div", class_="pb30")
        body = soup.find("div", class_="main-column")
        fpath = os.path.join(path, f"{name}.pdf")
        with tempfile.TemporaryDirectory() as tempdir:
            mdpath = os.path.join(tempdir, f"{name}.md")
            with open(mdpath, "w") as f:
                f.write(markdownify(str(header), strip=["img"]))
                f.write(
                    markdownify(str(body))
                    .replace("/assets", "https://www.policinglaw.info/assets")
                    .replace("\u0002", "")
                )  # Add original url to preserve download links.
            subprocess.run(
                [f"pandoc --pdf-engine=xelatex {mdpath} -o {fpath}"],
                shell=True,
            )


def main():
    output_path = "./output"
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    urls = collect_country_urls(BASE_URL)
    compile_pdfs(urls, output_path)


if __name__ == "__main__":
    main()
