# BioPortal utilities

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import urllib.parse
import os
from fnmatch import fnmatch

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

BIOPORTAL_API_BASE = "https://data.bioontology.org"


def annotate(api_key, text, ontologies=[], longest_only=False, expand_mappings=False, include=[]):
    """
    Makes a call to the NCBO Annotator
    :return: 
    :param api_key: 
    :param text: 
    :param ontologies: 
    :param longest_only: 
    :param expand_mappings:
    :param include: 
    :return: 
    """
    annotations = []
    url = BIOPORTAL_API_BASE + '/annotator'

    headers = {
        'content-type': "application/json",
        'authorization': "apikey token=" + api_key
    }

    if len(text) > 0:
        payload = {'text': text,
                   'longest_only': longest_only,
                   'expand_mappings': expand_mappings}

        if len(ontologies) > 0:
            payload['ontologies'] = ','.join(ontologies)

        if len(include) > 0:
            payload['include'] = ','.join(include)

        response = requests.post(url, json=payload, headers=headers, verify=False)

        if response.status_code != 200:
            raise Exception('Problem when calling the Annotator: ' + response.text)



        # print(payload)
        # print(response.url)
        # print(response.status_code)
        # print(response.text)
        annotations = json.loads(response.text)

    return annotations