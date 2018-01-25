#!/usr/bin/python

import sys
import json
import pystache
import requests
from dateutil import parser as dateparser
import dateutil

reload(sys)
sys.setdefaultencoding('utf-8')

GBIF = "https://api.gbif.org/v1/"

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

query = { 'publishingCountry': 'NO', 'limit': 500 }
response = requests.get(GBIF + "dataset/search", params=query).json()

datasets = []
sources = {}
for result in response['results']:
    data = requests.get(GBIF + "dataset/" + result['key']).json()
    source = data['installationKey']
    if not source in sources:
        sources[source] = requests.get(GBIF + "installation/" + source).json()

    # doesn't look like we can trust the record counts from the dataset search
    occurrences = requests.get(GBIF + "occurrence/search",
            params={ 'datasetKey': result['key'] }).json()
    datasets.append({
        'key': result['key'],
        'title': result['title'],
        'occurrenceCount': occurrences['count'],
        'installation': sources[source]['title'],
        'organization': result['publishingOrganizationTitle'],
        'type': result['type'].replace("_", " ").capitalize(),
        'created': dateparser.parse(data['created']).strftime("%Y-%m-%d"),
        'modified': dateparser.parse(data['modified']).strftime("%Y-%m-%d"),
    })

template = open("template.html", "r").read()
datasets = sorted(datasets, key=lambda k: (k['type'], k['title']))

renderer = pystache.Renderer()
html = renderer.render(template, { 'datasets': datasets })

print(html)

