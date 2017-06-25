# Sachsenscraper

Sachsenscraper is a tool to collect data about the members (MdL) of the regional parliament (Landtag) of the free state of Saxony (Freistaat Sachsen) in Germany. The data

## Setup

Install the requirements, which are

* requests
* BeautifulSoup4

e.g. by using pip:

```zsh
pip install -r requirements.txt
```

## Usage

### sachsenscraper.py

Call *./sachsenscraper.py* (without any further arguments) to fetch all MdL for all days the Landtag of Saxony existed.
A folder "scraped_data" needs to be provided, but can be configured in the *CONSTANTS* section in the upper part of the file. Some other options can be configured up there as well.

The data of every day scraped will be put into a file, which is named *%Y-%m-%d.json*. The format is (example):

```json
{
  "date": "2013-01-15",
  "mdls": [
            {
                "name": "Apfel, Holger (Nazischwein!)",
                "party": "NPD",
                "office": "",
                "gender": "m\u00e4nnlich",
                "religion": "konfessionslos",
                "family status": "verheiratet"
            },  ...
          ]
}
```

### sachsenexplorer.py

With *sachsenexplorer.py* you can then extract more useful information from the scraped data. Like the first day they
entered the parliament etc. this all will be written to some file...
