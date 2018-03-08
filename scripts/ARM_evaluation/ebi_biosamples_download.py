#!/usr/bin/python3

# Utility to download biosamples metadata from EBI's API and store them into a folder in multiple files

import json

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable InsecureRequestWarning

BIOSAMPLES_URL = 'https://www.ebi.ac.uk/biosamples/api/samples'
MAX_SIZE_PER_PAGE = 1000  # Max number of biosamples to retrieve per call (page). The API does not accept values higher than 1000
PAGES_PER_FILE = 10 # Number of pages that will be stored into each file
EBI_BIOSAMPLES_OUTPUT_FOLDER = "/Users/marcosmr/Dropbox/TMP_LOCATION/ARM_resources/ebi_biosamples/biosamples_original"  # Source NCBI Biosample instances
MAX_PAGES = -1  # Max number of pages to iterate over. -1 means no limit


def get_biosamples(page=0, size=MAX_SIZE_PER_PAGE):
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


def get_all_biosamples(max_pages=MAX_PAGES, pages_per_file=PAGES_PER_FILE):
    """
    Retrieves all the biosamples from EBI's BioSamples database and saves them to a folder in multiple files
    :param max_pages: 
    :param pages_per_file: 
    """
    biosamples_to_export = []
    start_page_range = 0
    current_page = 0
    first_call = True
    total_pages = 1 # just for the first call
    total_biosamples_count = 0
    #start_range_biosamples_count = 0
    while current_page < total_pages:
        response = get_biosamples(current_page)
        print(response.url)
        if response.status_code == 200:
            response_json = json.loads(response.text)
            # extract samples
            if response_json['_embedded'] is not None and response_json['_embedded']['samples'] is not None:
                biosamples_call = response_json['_embedded']['samples']
                biosamples_to_export = biosamples_to_export + biosamples_call
                total_biosamples_count = total_biosamples_count + len(biosamples_call)
                print('No. biosamples returned: ' + str(len(biosamples_call)))
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

            # save to file
            if current_page == start_page_range + (pages_per_file - 1):
                file_path = EBI_BIOSAMPLES_OUTPUT_FOLDER + "/ebi_biosamples_" + str((start_page_range * MAX_SIZE_PER_PAGE) + 1) \
                            + "to" + str((current_page + 1) * MAX_SIZE_PER_PAGE) + '.json'
                print('Limit reached. Page range: ' + str(start_page_range) + '-' + str(current_page))
                print('Saving ' + str(len(biosamples_to_export)) + ' biosamples to file: ' + file_path)

                # export to file
                with open(file_path, 'w') as outfile:
                    json.dump(biosamples_to_export, outfile)
                outfile.close()
                biosamples_to_export = []
                start_page_range = current_page + 1
                #start_range_biosamples_count = total_biosamples_count + 1

            current_page = current_page + 1
    print('Done. Total number of biosamples saved: ' + str(total_biosamples_count))


def main():
    get_all_biosamples()


if __name__ == "__main__": main()
