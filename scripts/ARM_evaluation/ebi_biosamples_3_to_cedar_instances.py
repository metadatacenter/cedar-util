# TODO

# !/usr/bin/python3

# ebi_biosamples_to_cedar.py: Utility to transform EBI BioSample metadata to CEDAR template instances. The resulting
# instances are saved to a local folder

import xml.etree.ElementTree as ET
from pprint import pprint
import json
from random import shuffle
import cedar_util
import os


# Class that represents a biosample object extracted from EBI's BioSamples database
class EbiBiosample:
    def __init__(self, accession=None, name=None, releaseDate=None, updateDate=None, organization=None, contact=None,
                 organism=None, age=None, sex=None, organismPart=None, cellLine=None, cellType=None,
                 diseaseState=None, ethnicity=None):
        self.accession = accession
        self.name = name
        self.releaseDate = releaseDate
        self.updateDate = updateDate
        self.organization = organization
        self.contact = contact
        self.organism = organism
        self.age = age
        self.sex = sex
        self.organismPart = organismPart
        self.cellLine = cellLine
        self.cellType = cellType
        self.diseaseState = diseaseState
        self.ethnicity = ethnicity


# Execution settings
EBI_BIOSAMPLES_LIMIT = 50000  # Number of biosamples to be transformed into instances

# Local folders
MAX_FILES_PER_FOLDER = 10000
OUTPUT_BASE_PATH = '/Users/marcosmr/tmp/ARM_resources/ebi_biosamples/cedar_instances'  # Path to save the CEDAR instances
OUTPUT_BASE_FILE_NAME = 'ebi_biosample_instance'
EBI_BIOSAMPLES_PATH = "/Users/marcosmr/tmp/ARM_resources/ebi_biosamples/biosamples_filtered"  # Source EBI biosamples
EMPTY_BIOSAMPLE_INSTANCE_PATH = '/Users/marcosmr/tmp/ARM_resources/ebi_biosamples/ebi_biosample_instance_empty.json'  # Empty CEDAR instance

# Other constants
EBI_BIOSAMPLE_BASIC_FIELDS = ['accession', 'name', 'releaseDate', 'updateDate', 'organization', 'contact']
EBI_BIOSAMPLE_ATTRIBUTES = ['organism', 'age', 'sex', 'organismPart', 'cellLine', 'cellType', 'diseaseState',
                            'ethnicity']

EBI_BIOSAMPLE_ALL_FIELDS = EBI_BIOSAMPLE_BASIC_FIELDS + EBI_BIOSAMPLE_ATTRIBUTES


# Function definitions
def extract_value(sample, field_name):
    value = None
    if field_name in sample:
        field_type = type(sample[field_name])
        if field_type == str:
            value = sample[field_name]
        elif field_type == list:
            value_obj = sample[field_name][0]
            if 'text' in value_obj:
                value = value_obj['text']
            elif 'name' in value_obj:
                value = value_obj['name']
            elif 'Name' in value_obj:
                value = value_obj['Name']
    return value


def read_ebi_biosamples(folder_path):
    """
    Parses all files in a folder and subfolders that contain EBI biosamples
    :param folder_path: 
    :return: A list of EbiBiosample objects
    """
    all_biosamples_list = []
    print('Reading EBI biosamples from folder: ' + folder_path)
    for f in sorted(os.listdir(folder_path)):
        if 'ebi_biosamples' in f and '.json' in f:  # basic check to be sure that we are processing the right files
            file_path = os.path.join(folder_path, f)
            samples_json = json.load(open(file_path, "r"))
            for sample in samples_json:
                biosample = EbiBiosample()
                # Basic fields
                for field_name in EBI_BIOSAMPLE_BASIC_FIELDS:
                    if field_name in sample and sample[field_name] is not None:
                        value = extract_value(sample, field_name)
                        setattr(biosample, field_name, value)

                # Other characteristics
                characteristics = sample['characteristics']
                if characteristics is not None:
                    for field_name in EBI_BIOSAMPLE_ATTRIBUTES:
                        if field_name in characteristics and len(characteristics[field_name]) > 0:
                            value = extract_value(characteristics, field_name)
                        else:
                            value = None
                        setattr(biosample, field_name, value)
                all_biosamples_list.append(biosample)

    limit = min(EBI_BIOSAMPLES_LIMIT, len(all_biosamples_list))

    print('Randomly picking ' + str(limit) + ' samples')
    shuffle(all_biosamples_list)  # Shuffle the list to ensure that we will return a sublist of random samples
    if limit < len(all_biosamples_list):
        selected_biosamples_list = all_biosamples_list[:limit]
    else:
        selected_biosamples_list = all_biosamples_list

    return selected_biosamples_list


def ebi_biosample_to_cedar_instance(ebi_biosample):
    """
    Translates an EbiBioSample object to a EBI Biosample CEDAR instance
    :param ebi_biosample: EbiBioSample object
    :return: A BioSample CEDAR instance
    """
    json_file = open(EMPTY_BIOSAMPLE_INSTANCE_PATH, "r")  # Open the JSON file for writing
    instance = json.load(json_file)  # Read the JSON into the buffer
    json_file.close()  # Close the JSON file

    # set field values
    for field_name in EBI_BIOSAMPLE_ALL_FIELDS:
        if field_name in instance:
            instance[field_name]['@value'] = getattr(ebi_biosample, field_name)
        else:
            raise KeyError('Field name not found in instance: ' + field_name)

    return instance


def save_to_folder(instance, instance_number, output_path):
    """
    Saves an instance to a local folder
    :param instance: 
    :param instance_number: Number used to name the output files
    :param output_path: 
    """
    output_file_path = output_path + "/" + OUTPUT_BASE_FILE_NAME + "_" + str(instance_number) + '.json'

    with open(output_file_path, 'w') as output_file:
        json.dump(instance, output_file, indent=4)


def main():
    biosamples_list = read_ebi_biosamples(EBI_BIOSAMPLES_PATH)
    instance_number = 0
    for biosample in biosamples_list:
        #pprint(vars(biosample))  # Print the biosample fields
        instance_number = instance_number + 1

        # Save to files
        start_index = ((instance_number - 1) // MAX_FILES_PER_FOLDER) * MAX_FILES_PER_FOLDER
        end_index = start_index + MAX_FILES_PER_FOLDER - 1
        output_path = OUTPUT_BASE_PATH + '/' + 'instances_' + str(start_index + 1) + 'to' + str(end_index + 1)

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        instance = ebi_biosample_to_cedar_instance(biosample)
        print('Saving instance #' + str(instance_number) + ' to ' + output_path)
        save_to_folder(instance, instance_number, output_path)


if __name__ == "__main__": main()
