#!/usr/bin/python3

# ncbi_biosample_to_cedar.py: Utility to transform NCBI BioSample metadata to CEDAR template instances.

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from random import shuffle
import cedar_util

# Class that represents a biological sample for the NCBI's BioSample Human Package 1.0
# https://submit.ncbi.nlm.nih.gov/biosample/template/?package=Human.1.0&action=definition
class NcbiBiosample:
    def __init__(self, sample_name=None, sample_title=None, bioproject_accession=None, organism=None, isolate=None,
                 age=None, biomaterial_provider=None, sex=None, tissue=None, cell_line=None, cell_subtype=None,
                 cell_type=None, culture_collection=None, dev_stage=None, disease=None, disease_stage=None,
                 ethnicity=None, health_state=None, karyotype=None, phenotype=None, population=None, race=None,
                 sample_type=None, treatment=None, description=None):
        self.sample_name = sample_name
        self.sample_title = sample_title
        self.bioproject_accession = bioproject_accession
        self.organism = organism
        self.isolate = isolate
        self.age = age
        self.biomaterial_provider = biomaterial_provider
        self.sex = sex
        self.tissue = tissue
        self.cell_line = cell_line
        self.cell_subtype = cell_subtype
        self.cell_type = cell_type
        self.culture_collection = culture_collection
        self.dev_stage = dev_stage
        self.disease = disease
        self.disease_stage = disease_stage
        self.ethnicity = ethnicity
        self.health_state = health_state
        self.karyotype = karyotype
        self.phenotype = phenotype
        self.population = population
        self.race = race
        self.sample_type = sample_type
        self.treatment = treatment
        self.description = description


# Execution settings
SAVE_TO_FOLDER = False
POST_TO_CEDAR = True
BIOSAMPLES_LIMIT = 5

# Local folders
OUTPUT_PATH = '/Users/marcosmr/Dropbox/TMP_LOCATION/ARM_resources/ncbi_biosample/cedar_instances'  # Path where the CEDAR instances will be saved
OUTPUT_BASE_FILE_NAME = 'ncbi_biosample_instance'
BIOSAMPLE_FILE_PATH = "/Users/marcosmr/Dropbox/TMP_LOCATION/ARM_resources/ncbi_biosample/biosample_result.xml"  # Source NCBI Biosample instances
EMPTY_BIOSAMPLE_INSTANCE_PATH = '/Users/marcosmr/Dropbox/TMP_LOCATION/ARM_resources/ncbi_biosample/ncbi_biosample_instance_empty.json'  # Empty CEDAR instance

# CEDAR connection settings
RESOURCE_SERVER = "https://resource.metadatacenter.orgx/"
TEMPLATE_ID = "https://repo.metadatacenter.orgx/templates/eef6f399-aa4e-4982-ab04-ad8e9635aa91"
TARGET_CEDAR_FOLDER_ID = "https://repo.metadatacenter.orgx/folders/2bd1c561-d899-4c91-bdf1-4be7c0687b96"

# Other constants
BIOSAMPLE_BASIC_FIELDS = ['biosample_accession', 'sample_name', 'sample_title', 'bioproject_accession', 'organism']
BIOSAMPLE_ATTRIBUTES = ['isolate', 'age', 'biomaterial_provider', 'sex', 'tissue', 'cell_line', 'cell_type',
                        'cell_subtype', 'culture_collection', 'dev_stage', 'disease', 'disease_stage',
                        'ethnicity', 'health_state', 'karyotype', 'phenotype', 'population', 'race',
                        'sample_type', 'treatment']
BIOSAMPLE_ALL_FIELDS = BIOSAMPLE_BASIC_FIELDS + BIOSAMPLE_ATTRIBUTES


# Functions definition

def get_attribute_value(attribute_node, attribute_name):
    """
    It extracts the attribute value from a BioSample attribute XML node
    :param attribute_node: 
    :param attribute_name: 
    :return: The attribute value
    """
    if attribute_node.get('attribute_name') == attribute_name \
            or attribute_node.get('harmonized_name') == attribute_name \
            or attribute_node.get('display_name') == attribute_name:
        return attribute_node.text
    else:
        return None


def read_ncbi_biosamples(file_path):
    """
    Parses an XML file with multiple NCBI biosamples
    :param file_path: 
    :return: A list of NcbiBiosample objects
    """
    all_biosamples_list = []
    print('Reading file: ' + file_path)
    tree = ET.parse(file_path)
    root = tree.getroot()
    num_biosamples = len(root.getchildren())
    limit = min(num_biosamples, BIOSAMPLES_LIMIT)  # Limit of biosamples that will be read
    print('Extracting all samples from file (no. samples: ' + str(num_biosamples) + ')')
    for child in root:
        biosample = NcbiBiosample()
        description_node = child.find('Description')
        attributes_node = child.find('Attributes')
        # print(ET.tostring(child))

        # sample name
        sample_ids = child.find('Ids')
        for sample_id in sample_ids:
            if sample_id.get('db_label') == 'Sample name':
                biosample.sample_name = sample_id.text
        # sample title
        if description_node is not None and description_node.find('Title') is not None:
            biosample.sample_title = description_node.find('Title').text
        # bioproject accession
        links = child.find('Links')
        if links is not None:
            for link in links:
                if link.get('target') == 'bioproject':
                    biosample.bioproject_accession = link.text
        # organism
        if description_node is not None:
            organism_node = description_node.find('Organism')
            if organism_node is not None and organism_node.find('OrganismName') is not None:
                biosample.organism = organism_node.find('OrganismName').text
        # attributes
        for att in attributes_node:
            for att_name in BIOSAMPLE_ATTRIBUTES:
                value = get_attribute_value(att, att_name)
                if value is not None:
                    setattr(biosample, att_name, value)
        # description
        if description_node is not None:
            comment_node = description_node.find('Comment')
            if comment_node is not None:
                if comment_node.find('Paragraph') is not None:
                    biosample.description = comment_node.find('Paragraph').text

        all_biosamples_list.append(biosample)

    if limit < num_biosamples:
        print('Randomly picking ' + str(limit) + ' samples')
        shuffle(all_biosamples_list)  # Shuffle the list to ensure that we will return a sublist of random samples
        selected_biosamples_list = all_biosamples_list[:limit]
    else:
        selected_biosamples_list = all_biosamples_list

    return selected_biosamples_list


def ncbi_biosample_to_cedar_instance(ncbi_biosample):
    """
    Translates an NcbiBiosample object to a NCBI Biosample CEDAR instance
    :param ncbi_biosample: NcbiBiosample object
    :return: A BioSample CEDAR instance
    """
    json_file = open(EMPTY_BIOSAMPLE_INSTANCE_PATH, "r")  # Open the JSON file for writing
    instance = json.load(json_file)  # Read the JSON into the buffer
    json_file.close()  # Close the JSON file

    # set field values
    for field_name in BIOSAMPLE_ALL_FIELDS:
        if field_name in instance:
            instance[field_name]['@value'] = getattr(ncbi_biosample, field_name)
        else:
            raise KeyError('Field name not found in instance: ' + field_name)

    return instance


def save_to_folder(instance, instance_number):
    """
    Saves an instance to a local folder
    :param instance: 
    :param instance_number: Number used to name the output files
    :param folder_path: 
    """
    output_file_path = OUTPUT_PATH + "/" + OUTPUT_BASE_FILE_NAME + "_" + str(instance_number)
    with open(output_file_path, 'w') as output_file:
        json.dump(instance, output_file, indent=4)


def main():
    # Read api key from command line
    parser = argparse.ArgumentParser()
    parser.add_argument("apiKey", help="Your CEDAR apiKey")
    args = parser.parse_args()
    api_key= args.apiKey

    # Remove all existing instances for the template
    if POST_TO_CEDAR:
        print('Removing all instances of the template from CEDAR (templateId: ' + TEMPLATE_ID + ')')
        cedar_util.delete_instances_from_template(RESOURCE_SERVER, TEMPLATE_ID, sys.maxsize, 500, api_key)

    # Read biosamples from XML file
    biosamples_list = read_ncbi_biosamples(BIOSAMPLE_FILE_PATH)
    instance_number = 0
    for biosample in biosamples_list:
        # pprint(vars(biosample)) # Print the biosample fields
        instance_number = instance_number + 1
        instance = ncbi_biosample_to_cedar_instance(biosample)
        if SAVE_TO_FOLDER:
            print('Saving instance #' + str(instance_number))
            save_to_folder(instance, instance_number)
        if POST_TO_CEDAR:
            print('Posting instance #' + str(instance_number))
            cedar_util.post_instance(instance, TEMPLATE_ID, RESOURCE_SERVER, TARGET_CEDAR_FOLDER_ID, api_key)


if __name__ == "__main__": main()
