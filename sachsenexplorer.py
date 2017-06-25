#!/usr/bin/env python3
"""
Explore scraped data from the saxony regional parliament.
"""

import os
import json
import pickle
import requests

from sachsenscraper import SAVE_DIR

__author__ = "Olf Tuksowitsch <olf@subsignal.org"
__license__ = "GPL V3"

# CONSTANTS ############################################################################################################

ITEM_BY_TITLE_URL = "https://www.wikidata.org/wiki/Special:ItemByTitle?site=dewiki&page={name}"

KEYS = ['name', 'qvalue', 'entry_date']

OUTFILE_NAME = "clean_names.json"

# FUNCTIONS ############################################################################################################

def load_data():
    """
    Reads all scraped data and loads it into one big list
    """
    file_list = os.listdir(SAVE_DIR)
    file_list.sort()
    all_data = []
    no_of_files = len(file_list)
    for i, one_file in enumerate(file_list):
        with open(os.path.join(SAVE_DIR, one_file), 'r') as infile:
            data = json.load(infile)
        all_data.append(data)
        if i%123 == 0:
            print("{0}/{1}".format(i, no_of_files-1), end="\r")
    print("{0}/{1}".format(i, no_of_files-1), end="\r")
    print("")
    return all_data

def reformat(name):
    """
    TODO: Am komma splitten danach strippen usw. usf.
    """
    # Filter out academic titles
    name = name.replace("Dr. h.c.", "").replace("Prof.", "").replace("Dr.", "").strip()
    name_parts = name.split(',')[::-1]
    name_parts[0] =  name_parts[0].lstrip()
    return " ".join(name_parts)

def extract_names(all_data):
    """
    Generates a list of all MdLs ordered by their entry date.
    Every MdL in this list is unique.
    """
    mdls = []
    mdls_data = []
    for day in all_data:
        for mdl in day['mdls']:
            name = reformat(mdl['name'])
            entry_date = day['date']
            try:
                mdls.index(name)
            except ValueError:
                q_value = find_q_value(name)
                print("On {entry_date}: {name} - {q_value}".format(name=name,
                                                                     entry_date=entry_date,
                                                                     q_value=q_value))
                mdls.append(name)
                mdls_data.append(dict(zip(KEYS, [name, q_value, entry_date])))
    return mdls_data

def find_q_value(name):
    """
    Tries to match a name from the members of the Landtag of Saxony List with existing wikidata entries and returns
    the Q number if a matching entry was found. The detection works based on a HTTP 302 which is raised, when an
    entry was found (in contrast to HTTP 200). It's hacky, but seems to work somehow. Surprisingly.
    """
    url = ITEM_BY_TITLE_URL.format(name=reformat(name))
    try:
        r = requests.get(url, allow_redirects=False)
    except:
        print("--> Could not fetch Q-Value")
        return ""
    if r.is_redirect:
        return r.headers['Location']
    else:
        return ""

def save_clean_names_and_q(name_list, outfile_name=OUTFILE_NAME):
    """
    Saves a json object, or to be exact: Some python object that can be searialized as a json-object.
    """
    with open(outfile_name, 'w') as outfile:
        json.dump(name_list, outfile)
    return outfile_name

# MAIN #################################################################################################################

if __name__ == "__main__":
    all_data = load_data()
    json_names = extract_names(all_data)
    save_clean_names_and_q(json_names)
