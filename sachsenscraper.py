#!/usr/bin/env python3
"""
This tool scrapes the members (MdL) of the regional government (Landtag) of the federal state of Saxony in Germany.
The data is provided by the state of Saxony and can be queried via URL.
"""

import sys
import datetime
import json
import requests

from time import sleep
from multiprocessing import Pool
from bs4 import BeautifulSoup


__author__ = "Olf Tuksowitsch <olf@subsignal.org>"
__license__ = "GPL V3"


# CONSTANTS ############################################################################################################

# Fetching "Intensity"
FETCH_URL = "http://www.landtag.sachsen.de/de/abgeordnete-fraktionen\
/abgeordnete/statistik?datestring={date}&submitDate=true"
FETCH_RETRY = 10
FETCH_SLEEP = 0.3

# Scraping Configuration
# Coucils which MdLs can be member of
COUNCIL_ID      = "CouncilsSelected"
COUNCIL_LIST    =   {   "109" : "G10-Kommission" ,
                        "108" : "Parlamentarische Kontrollkommission",
                        "130" : "Parlamentarisches Kontrollgremium"}

# Comittees which MdLs can be member of
COMITTEE_ID     =   "CommitteesSelected"
COMITTEE_LIST   =   {   "132" : "Ausschuss für Geschäftsordnung und Immunitätsangelegenheiten",
                        "124" : "Ausschuss für Schule und Sport",
                        "128" : "Ausschuss für Soziales und Verbraucherschutz, Gleichstellung und Integration",
                        "126" : "Ausschuss für Umwelt und Landwirtschaft",
                        "135" : "Ausschuss für Wirtschaft, Arbeit und Verkehr",
                        "129" : "Ausschuss für Wissenschaft und Hochschule, Kultur und Medien",
                        "136" : "Bewertungsausschuss",
                        "141" : "Enquete-Kommission „Sicherstellung der Versorgung und Weiterentwicklung\
 der Qualität in der Pflege älterer Menschen im Freistaat Sachsen“",
                        "130" : "Europaausschuss",
                        "134" : "Haushalts- und Finanzausschuss",
                        "127" : "Innenausschuss",
                        "131" : "Petitionsausschuss",
                        "133" : "Verfassungs- und Rechtsausschuss",
                        "121" : "Wahlprüfungsausschuss",
                        "140" : "1. Untersuchungsausschuss („Neonazistische Terrornetzwerke in Sachsen“)"}

# Table Keys of the MdL-table
KEYS = ["name", "party", "office", "gender", "religion", "family status"]

# Default Dates to scrape - for saxony its the first day the parliament exists until today
START_DATE  = datetime.date(1990, 10, 27)
END_DATE    = datetime.datetime.now().date()

# Directories where scraped data is saved to and where errors are written to
SAVE_DIR = "scraped_data"
ERROR_FILE = "error.log"

# Error Messages
PARSE_ERROR = "{single_date}: Could not parse server response, or server sent no response at all.\n"
FETCH_ERROR = "{single_date}: Error during fetch.\n"

# Enable Debugging Functions such as more verbose output, early termination of loops etc.
DEBUGGING   = True

# FUNCTIONS ############################################################################################################

def daterange(start_date=START_DATE, end_date=END_DATE):
    """
    Generator yielding all days in from a specified
    start date to a specified end date
    """
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


def fetch_content(url, retry_count=0, fetch_retry=FETCH_RETRY, fetch_sleep=FETCH_SLEEP):
    """
    Fetches the actual content and raises an exception if the request was not successful.
    """
    if retry_count > fetch_retry:
        raise ConnectionError
    page = requests.get(url)
    if not page.status_code == 200:
        sleep(fetch_sleep)
        retry_count+=1
        fetch_content(url, retry_count, fetch_retry, fetch_sleep)
    return page.text


def parse_content(content):
    """
    Parses the HTML Response and returns a list of dict with all
    data. If the response contains no data, it will exit the
    program as it is likely, that a rate limit was reached.
    """
    data = []
    mdl_table = BeautifulSoup(content, 'html.parser').tbody

    try:
        in_rows = mdl_table.find_all('tr')
    except AttributeError:
        raise

    for in_row in in_rows:
        out_row = []
        for cell in in_row.find_all('td'):
            out_row.append(cell.text)
        if not len(out_row):
            continue
        data.append(dict(zip(KEYS, out_row)))
    return data


def write_error(error_message, error_file=ERROR_FILE, print_message=True):
    """
    Writes an Error Message to the specified location and file.
    """
    with open(error_file, 'a') as e_file:
        e_file.write(error_message)
    print("\n"+error_message)
    return


def build_result(single_date):
    """
    Performs fetching, converting, saving for one specified date
    """
    if DEBUGGING:
        print(single_date, end="\r")
    fetch_url = FETCH_URL.format(date=single_date.strftime("%d.%m.%Y"))

    # If no content is returned, the fetch failed.
    try:
        content = fetch_content(fetch_url)
    except:
        write_error(FETCH_ERROR.format(single_date=single_date))
        return

    # If the parser gives no result, the result builder exits early
    # This is the case, if the response from the server contains
    # no table
    try:
        mdl_data = parse_content(content)
    except AttributeError:
        write_error(PARSE_ERROR.format(single_date=single_date))
        return

    result = {  'date' : single_date.strftime("%Y-%m-%d"),
                'mdls' : mdl_data}

    with open("{save_dir}/{date}.json".format(save_dir=SAVE_DIR, date=single_date), "w") as save_file:
        json.dump(result, save_file)

    return


def scrape_sachsen(start_date=START_DATE, end_date=END_DATE, councils=False, comittees=False):
    """
    Scraping Wrapper, handles all the scraping tasks.
    """

    # Handle non existing functionality
    if not councils == False: raise NotImplementedError("Councils cannot be fetched yet.")
    if not comittees == False: raise NotImplementedError("Comittees cannot be fetched yet.")

    # Fetch data
    for single_date in daterange(start_date, end_date):
        build_result(single_date)

# __MAIN__ #############################################################################################################

if __name__ == "__main__":
    scrape_sachsen(start_date)
