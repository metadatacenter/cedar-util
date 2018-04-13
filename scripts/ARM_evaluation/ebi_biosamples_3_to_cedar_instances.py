# TODO

# !/usr/bin/python3

# ebi_biosamples_to_cedar.py: Utility to transform EBI BioSample metadata to CEDAR template instances. The resulting
# instances are saved to a local folder

import json
import os
from random import shuffle
import uuid

import arm_evaluation_util
import datasources_util


# Class that represents a biosample object extracted from EBI's BioSamples database
class EbiBiosample:
    def __init__(self, ids=None, accession=None, name=None, releaseDate=None, updateDate=None, organization=None,
                 contact=None, organism=None, age=None, sex=None, organismPart=None, cellLine=None, cellType=None,
                 diseaseState=None, ethnicity=None):
        # This set of ids will be used to store the ids of the samples used for testing, in order to exclude those
        # samples when creating the training dataset when doing an evaluation across EBI and NCBI dbs
        self.ids = ids
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


"""
MAIN EXECUTION SETTINGS
"""
TRAINING_SET_SIZE = 0
TESTING_SET_SIZE = 20000
MAX_FILES_PER_FOLDER = 10000

# Input
INPUT_PATH = '/Users/marcosmr/tmp/ARM_resources/ebi_biosamples/biosamples_filtered/homo_sapiens-min_3_attribs_valid'

# Output
OUTPUT_BASE_PATH = '/Users/marcosmr/tmp/ARM_resources/cedar_instances_tmp/'

TRAINING_BASE_PATH = OUTPUT_BASE_PATH + '/1_training'
TESTING_BASE_PATH = OUTPUT_BASE_PATH + '/2_testing'
EXCLUDE_TESTING_IDS = True
EXCLUDED_IDS_FILE_PATH = '/Users/marcosmr/tmp/ARM_resources/evaluation_results/2018_03_27_5-training_124200_ebi-testing-13800_ebi_NOSTRICT_BASELINE/training_ids.txt'

"""
CONSTANTS
"""
OUTPUT_BASE_FILE_NAME = 'ebi_biosample_instance'
EMPTY_BIOSAMPLE_INSTANCE_PATH = '/Users/marcosmr/tmp/ARM_resources/ebi_biosamples/ebi_biosample_instance_empty.json'  # Empty CEDAR instance
EBI_BIOSAMPLE_BASIC_FIELDS = ['accession', 'name', 'releaseDate', 'updateDate', 'organization', 'contact']
EBI_BIOSAMPLE_ATTRIBUTES = ['organism', 'age', 'sex', 'organismPart', 'cellLine', 'cellType', 'diseaseState',
                            'ethnicity']

EBI_BIOSAMPLE_ALL_FIELDS = EBI_BIOSAMPLE_BASIC_FIELDS + EBI_BIOSAMPLE_ATTRIBUTES


# Function definitions

def extract_ebi_ids(sample):
    """
    It extracts all the ids from the sample
    :param sample: 
    """
    ids = set()

    accession_field = 'accession'
    value = datasources_util.extract_ebi_value(sample, accession_field)
    if datasources_util.is_valid_value(value):
        ids.add(value)

    external_references_field = 'external_references'
    if external_references_field in sample and sample[external_references_field] is not None:
        refs = sample[external_references_field]
        for ref in refs:
            if 'acc' in ref and ref['acc'] is not None:
                value = ref['acc']
                if datasources_util.is_valid_value(value):
                    ids.add(value)
    return ids


def read_ebi_biosamples(folder_path, max=TRAINING_SET_SIZE + TESTING_SET_SIZE):
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
                biosample.ids = set()

                # Save ids
                biosample.ids.update(extract_ebi_ids(sample))

                # Basic fields
                for field_name in EBI_BIOSAMPLE_BASIC_FIELDS:
                    if field_name in sample and sample[field_name] is not None:
                        value = datasources_util.extract_ebi_value(sample, field_name)
                        if datasources_util.is_valid_value(value):
                            setattr(biosample, field_name, value)

                # Other characteristics
                characteristics = sample['characteristics']
                if characteristics is not None:
                    for field_name in EBI_BIOSAMPLE_ATTRIBUTES:
                        if field_name in characteristics and len(characteristics[field_name]) > 0:
                            value = datasources_util.extract_ebi_value(characteristics, field_name)
                            if datasources_util.is_valid_value(value):
                                setattr(biosample, field_name, value)

                all_biosamples_list.append(biosample)

    limit = min(max, len(all_biosamples_list))
    print('Total no. samples: ' + str(len(all_biosamples_list)))
    print('Randomly picking ' + str(limit) + ' samples')
    shuffle(all_biosamples_list)  # Shuffle the list to ensure that we will return a sublist of random samples
    return all_biosamples_list[:limit]


def ebi_biosample_to_cedar_instance(ebi_biosample):
    """
    Translates an EbiBioSample object to a EBI Biosample CEDAR instance
    :param ebi_biosample: EbiBioSample object
    :return: A BioSample CEDAR instance
    """
    json_file = open(EMPTY_BIOSAMPLE_INSTANCE_PATH, "r")  # Open the JSON file for writing
    instance = json.load(json_file)  # Read the JSON into the buffer
    json_file.close()  # Close the JSON file

    if '@id' not in instance: # Generate @id if it's not there
        instance['@id'] = str(uuid.uuid4())

    # set field values
    for field_name in EBI_BIOSAMPLE_ALL_FIELDS:
        if field_name in instance:
            instance[field_name]['@value'] = getattr(ebi_biosample, field_name)
        else:
            raise KeyError('Field name not found in instance: ' + field_name)

    return instance


def main():
    if EXCLUDE_TESTING_IDS:
        excluded_ids = set(line.strip() for line in open(EXCLUDED_IDS_FILE_PATH))
    excluded_samples_count = 0
    # Read biosamples
    biosamples_list = read_ebi_biosamples(INPUT_PATH)
    testing_ids = set()
    training_ids = set()
    instance_number = 1
    for biosample in biosamples_list:

        # pprint(vars(biosample)) # Print the biosample fields
        if instance_number <= TRAINING_SET_SIZE:  # Training set
            output_folder = TRAINING_BASE_PATH
            training_ids.update(biosample.ids)

        elif instance_number <= (TRAINING_SET_SIZE + TESTING_SET_SIZE):  # Testing set
            output_folder = TESTING_BASE_PATH
            testing_ids.update(biosample.ids)
        else:  # Done, finish execution
            break

        instance = ebi_biosample_to_cedar_instance(biosample)

        # Generate output path
        start_index = (instance_number // MAX_FILES_PER_FOLDER) * MAX_FILES_PER_FOLDER
        end_index = start_index + MAX_FILES_PER_FOLDER - 1
        output_path = output_folder + '/' + 'instances_' + str(start_index + 1) + 'to' + str(end_index + 1)

        # Save instances
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        if not EXCLUDE_TESTING_IDS or (EXCLUDE_TESTING_IDS and (len(biosample.ids.intersection(excluded_ids))) == 0):
            if (instance_number % 1000) == 0:
                print('Saving instance #' + str(instance_number) + ' to ' + output_path)
            arm_evaluation_util.save_to_folder(instance, instance_number, output_path, OUTPUT_BASE_FILE_NAME)
            instance_number = instance_number + 1
        elif EXCLUDE_TESTING_IDS and (len(biosample.ids.intersection(excluded_ids))) > 0:
            print('Excluding: ' + str(biosample.ids.intersection(excluded_ids)))
            excluded_samples_count = excluded_samples_count + 1

    # Save training ids
    with open(OUTPUT_BASE_PATH + '/training_ids.txt', 'w') as output_file:
        for training_id in training_ids:
            output_file.write("%s\n" % training_id)

    # Save testing ids
    with open(OUTPUT_BASE_PATH + '/testing_ids.txt', 'w') as output_file:
        for testing_id in testing_ids:
            output_file.write("%s\n" % testing_id)

    print('No. of excluded samples: ' + str(excluded_samples_count))
    print('Finished')


if __name__ == "__main__": main()


