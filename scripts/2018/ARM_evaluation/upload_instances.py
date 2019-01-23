#!/usr/bin/python3

# Utility to upload instances of a template stored in a local folder to CEDAR

import cedar_util

CEDAR_URL = "https://resource.metadatacenter.orgx/"
API_KEY = ""
FOLDER_PATH = "/Users/marcosmr/Desktop/tmp/upload_test/"
TEMPLATE_ID = "https://repo.metadatacenter.orgx/templates/af87320c-faef-4af3-9323-28e08c0349d2"
TARGET_CEDAR_FOLDER_ID = "https://repo.metadatacenter.orgx/folders/b0513136-46b0-4cb2-8abc-624c2f3b027c"

def main():
    cedar_util.upload_instances(CEDAR_URL, FOLDER_PATH, TEMPLATE_ID, TARGET_CEDAR_FOLDER_ID, API_KEY)

if __name__ == "__main__": main()
