#!/usr/bin/python3

# Utilities to interact with EBI's API

import json

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable InsecureRequestWarning

BIOSAMPLES_URL = 'https://www.ebi.ac.uk/biosamples/api/samples'
MAX_SIZE = 1000;
EBI_BIOSAMPLES_OUTPUT_PATH = "resources/ebi_biosamples/ebi_biosamples.json"  # Source NCBI Biosample instances


def get_biosamples(page=0, size=MAX_SIZE):
    """
    Makes a call to EBI's BioSamples endpoint to retrieve biosamples metadata
    :param page: 
    :param size: 
    :return: 
    """
    querystring = {"page": page, "size": size}
    response = requests.request("GET", BIOSAMPLES_URL, params=querystring, verify=False)
    return response
    # print("GET instances summary URL: " + str(response.url))
    # print("GET instances summary response: " + str(response.status_code))
    return response


def get_all_biosamples(max_pages=-1):
    """
    Retrieves all the biosamples from EBI's BioSamples database and saves them to a file
    :param max_pages: 
    """
    all_biosamples = []
    page = 0
    total_pages = 1
    first_call = True
    while page < total_pages:
        response = get_biosamples(page)
        print(response.url)
        if response.status_code == 200:
            response_json = json.loads(response.text)

            # extract samples
            if response_json['_embedded'] is not None and response_json['_embedded']['samples'] is not None:
                biosamples = response_json['_embedded']['samples']
                all_biosamples = all_biosamples + biosamples
                print('No. biosamples extracted: ' + str(len(all_biosamples)))
            else:
                raise KeyError('biosamples not found')

            if first_call:
                if response_json['page'] is not None and response_json['page']['totalPages'] is not None:
                    total_pages = response_json['page']['totalPages']
                    if max_pages != -1:  # max_pages has been set
                        total_pages = max_pages
                    first_call = False
                else:
                    raise KeyError('totalPages not found')

            page = page + 1

    print('Total no. biosamples extracted: ' + str(len(all_biosamples)))
    # export to file
    with open(EBI_BIOSAMPLES_OUTPUT_PATH, 'w') as outfile:
        json.dump(all_biosamples, outfile)
    outfile.close()


def main():
    get_all_biosamples(1)


if __name__ == "__main__": main()
