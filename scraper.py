"""
Scrapes country profiles at https://www.policinglaw.info/.
"""

import os
import tempfile
import subprocess
from typing import List
import pandas as pd
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify
from alive_progress import alive_it
from hdx.location.country import Country

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


def parse_page(country_urls: List[str], path: str) -> None:
    """Compiles page to pdf, scores to csv."""
    country_compatibility = {}
    for url in alive_it(country_urls):
        name = url.split("/")[-2]
        soup = BeautifulSoup(requests.get(url=url).content, "html.parser")
        header = soup.find("div", class_="pb30")
        compatibility = header.find("img")["alt"]
        body = soup.find("div", class_="main-column")
        fpath = os.path.join(path, f"{name}.pdf")
        with tempfile.TemporaryDirectory() as tempdir:
            mdpath = os.path.join(tempdir, f"{name}.md")
            with open(mdpath, "w") as f:
                f.write(
                    markdownify(str(header), strip=["img"]).replace(
                        "standards:",
                        f"standards: {compatibility}",
                    )
                )
                f.write(
                    markdownify(str(body))
                    .replace("/assets", "https://www.policinglaw.info/assets")
                    .replace("\u0002", "")
                    .replace("Treaties|", "Treaties| | \n --- | --- \n")
                )  # Add original url to preserve download links.
            cmd = (
                "pandoc --pdf-engine=xelatex -V geometry:margin=1in"
                f" {mdpath} -o {fpath}"
            )
            subprocess.run([cmd], shell=True)
        # Separately collect the compatibility scores.
        country_compatibility[name] = compatibility
    df = pd.get_dummies(pd.DataFrame(country_compatibility, index=["score"]).T)
    df["isoab3"] = df.apply(
        lambda row: Country.get_iso3_country_code_fuzzy(row.name)[0], axis=1
    )
    # Western Sahara not recognized.
    df.loc[df.index == "sahrawi-arab-democratic-republic", "iso"] = "ESH"
    df.to_csv(os.path.join(path, "country_compatibilities.csv"))


def main():
    output_path = "./output"
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    urls = collect_country_urls(BASE_URL)
    parse_page(urls, output_path)


if __name__ == "__main__":
    main()
