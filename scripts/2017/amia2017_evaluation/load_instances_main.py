#!/usr/bin/python

# Created:      Mar-6-2017
# Last updated: Mar-6-2017
# main.py: Utility to load all instances in a folder to the CEDAR system

import time
import cedar_util

RESOURCE_SERVER = "https://resource.metadatacenter.orgx/"
API_KEY = "<api_key>"
TEMPLATE_ID = "https://repo.metadatacenter.orgx/templates/31338972-e0cd-4540-a0e3-ba809690bbab"
ROOT_FOLDER = "/Users/marcosmr/Desktop/tmp/Biosample_instances/annotated"
TARGET_CEDAR_FOLDER_ID = "https://repo.metadatacenter.orgx/folders/bb90e5b2-e4d3-4297-99fc-886101933d2a"
MAX_COUNT = 40000
LIMIT_PER_CALL = 500


def main():

    start_time = time.time()

    cedar_util.delete_instances_from_template(RESOURCE_SERVER, TEMPLATE_ID, MAX_COUNT, LIMIT_PER_CALL, API_KEY)
    cedar_util.load_instances_from_folder(RESOURCE_SERVER, ROOT_FOLDER, TEMPLATE_ID, TARGET_CEDAR_FOLDER_ID, API_KEY)

    print("\nExecution time:  %s seconds " % (time.time() - start_time))


if __name__ == "__main__": main()
