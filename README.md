# plscraper

Scrapes country profiles at https://www.policinglaw.info/.

## Installation and usage

First, `cd` into this project's directory and set up a virtual environment by running the following in your command line:
```
virtualenv plscraper
```
Activate your virtual environment with:
```
source plscraper/bin/activate
```
Install the dependencies with:
```
pip install -r requirements.txt
```
You'll also need Pandoc for the document conversion. Assuming you're on macOS, get it through homebrew:
```
brew install pandoc
```
After this you should be good to go! Run the scraper with:
```
python scraper.py
```
It will produce a pdf of each country's profile page under /outputs, along with a csv containing the countries' compatibility scores.
