#!/usr/bin/python3

# Utility to annotate keywords using the NCBO Annotator

import json
import time
import os
import sys
import term_normalizer

import bioportal_util

# Input
UNIQUE_VALUES_FILE_PATH = '/Users/marcosmr/tmp/ARM_resources/annotation_results/unique_values_lowercase.txt'

# Output
UNIQUE_VALUES_ANNOTATED_FILE_PATH = '/Users/marcosmr/tmp/ARM_resources/annotation_results/unique_values_annotated.txt'

# Settings
BIOPORTAL_API_KEY = ''
VALUES_PER_ITERATION = 2000

# List of relevant ontologies. The algorithm will try to pick pref_class_label and pref_class_uri from one of these
# ontologies. If that's not possible, it will pick values from any other ontologies
PREFERRED_ONTOLOGIES = ['EFO', 'DOID', 'PATO', 'OBI', 'CL', 'CLO', 'CHEBI', 'BFO', 'PR', 'CPT', 'MEDDRA', 'UBERON',
                        'RXNORM', 'SNOMEDCT', 'FMA', 'LOINC', 'NDFRT', 'EDAM', 'RCD', 'ICD10CM', 'SNMI', 'BTO',
                        'MESH', 'NCIT', 'OMIM']

NORMALIZED_VALUES_FILE_NAME = 'normalized_values.json'  # We assume that the file is stored in the current path

LIMIT_ANNOTATOR_TO_PREFERRED_ONTOLOGIES = False


# Class that represents a biosample object extracted from EBI's BioSamples database
class KeywordAnnotation:
    def __init__(self, keyword=None, pref_class_uri=None, pref_class_label=None, pref_class_ontology=None,
                 class_uris=set(), class_labels=set()):
        self.keyword = keyword
        self.pref_class_uri = pref_class_uri
        self.pref_class_label = pref_class_label
        self.pref_class_ontology = pref_class_ontology
        self.class_uris = class_uris
        self.class_labels = class_labels

    def obj_dict(self):
        result = {}
        result['keyword'] = self.keyword
        result['pref_class_uri'] = self.pref_class_uri
        result['pref_class_label'] = self.pref_class_label
        result['pref_class_ontology'] = self.pref_class_ontology
        result['class_uris'] = list(self.class_uris)
        result['class_labels'] = list(self.class_labels)
        return result


def get_ontology_id(annotation):
    """
    Get the ontology acronym from the annotation information
    :param annotation: 
    :return: 
    """
    ontology_link = annotation['annotatedClass']['links']['ontology']
    ontology_id = ontology_link.replace('http://data.bioontology.org/ontologies/', '')
    return ontology_id


def ontology_has_more_priority(ont1, ont2, ontologies_priority=PREFERRED_ONTOLOGIES):
    """
    Checks if ont1 has more priority than ont2 according to a defined list of priorities
    :param ont1: 
    :param ont2: 
    :param ontologies_priority: 
    :return: 
    """
    if ont1 in ontologies_priority:
        if ont2 in ontologies_priority:
            if ontologies_priority.index(ont1) < ontologies_priority.index(ont2):
                return True
        else:
            return True
    else:
        return False


def extract_keyword_annotations(keywords, annotations):
    """
    
    :param keywords: set of input keywords
    :param annotations: annotations coming from the NCBO Annotator output   
    """
    keyword_annotations = []
    for keyword in keywords:
        keyword_annotation = KeywordAnnotation(keyword)
        # Initialize sets
        keyword_annotation.class_labels = set()
        keyword_annotation.class_uris = set()
        for annotation in annotations:
            # I will pass a set of unique keywords and will keep the longest annotation so the array of annotations
            # will just contain an annotation
            specific_annotation = annotation['annotations'][0]
            if keyword.upper() == specific_annotation['text'].upper():
                class_uri = annotation['annotatedClass']['@id']
                class_ontology_id = get_ontology_id(annotation)
                if 'prefLabel' in annotation['annotatedClass']:
                    class_label = annotation['annotatedClass']['prefLabel'].upper()

                    if keyword_annotation.pref_class_label is None:  # First iteration
                        keyword_annotation.pref_class_label = class_label
                        keyword_annotation.pref_class_uri = class_uri
                        keyword_annotation.pref_class_ontology = class_ontology_id
                    else:
                        # Check if this ontology has more priority
                        if ontology_has_more_priority(class_ontology_id, keyword_annotation.pref_class_ontology):
                            # Add the prefered class to the list of classes and set the new one as preferred
                            keyword_annotation.class_labels.add(keyword_annotation.pref_class_label)
                            keyword_annotation.class_uris.add(keyword_annotation.pref_class_uri)
                            keyword_annotation.pref_class_label = class_label
                            keyword_annotation.pref_class_uri = class_uri
                            keyword_annotation.pref_class_ontology = class_ontology_id
                        else:  # Does not have more priority that the currently selected as preferred
                            keyword_annotation.class_labels.add(class_label)
                            keyword_annotation.class_uris.add(class_uri)
                else:
                    print('PrefLabel not found for class: ' + class_uri + '. It has been ignored')

        if keyword_annotation.pref_class_uri is not None:  # Check if we found at least one annotation for the keyword
            keyword_annotations.append(keyword_annotation)

    return keyword_annotations


def main():
    # Read unique values
    with open(UNIQUE_VALUES_FILE_PATH) as f:
        all_values = f.read().splitlines()

    # Test data
    #all_values = ['m', 'male']

    # Load file with normalized values
    norm_values = json.loads(open(os.path.join(sys.path[0], NORMALIZED_VALUES_FILE_NAME)).read())

    # Translates some specific values that the NCBO Annotator is not able to annotate to a value that the Annotator will annotate
    all_values_normalized = []

    for value in all_values:
        normalized_value = term_normalizer.normalize_value(value, norm_values)
        if normalized_value not in all_values_normalized:
            all_values_normalized.append(normalized_value)

    # Create lists of input keywords to avoid making big queries to the Annotator
    input_keywords_lists = []
    keywords = set()
    for value in all_values_normalized:
        if len(keywords) < VALUES_PER_ITERATION:
            keywords.add(value)
        elif len(keywords) == VALUES_PER_ITERATION:
            input_keywords_lists.append(keywords)
            keywords = set()
    # Add remaining keywords to the list
    if len(keywords) > 0:
        input_keywords_lists.append(keywords)

    unique_values_annotated = {}

    total_count = 0
    print('Annotation process started...')

    for keywords_list in input_keywords_lists:

        time.sleep(.150)  # wait between calls to the Annotator

        ontologies = []
        if LIMIT_ANNOTATOR_TO_PREFERRED_ONTOLOGIES:
            ontologies = PREFERRED_ONTOLOGIES

        annotations = bioportal_util.annotate(BIOPORTAL_API_KEY, ",".join(keywords_list), ontologies, longest_only=True,
                                              expand_mappings=True, include=['prefLabel'])
        keyword_annotations = extract_keyword_annotations(keywords_list, annotations)

        for ann in keyword_annotations:
            annotation_key = ann.keyword

            if annotation_key not in unique_values_annotated:
                unique_values_annotated[annotation_key] = KeywordAnnotation.obj_dict(ann)
            else:
                print('Keyword already there: ' + annotation_key)

        total_count = total_count + 1
        print('Total lists of keywords processed: ' + str(total_count) + '/' + str(len(input_keywords_lists)))

    # Write to file
    with open(UNIQUE_VALUES_ANNOTATED_FILE_PATH, 'w') as outfile:
        json.dump(unique_values_annotated, outfile)


if __name__ == "__main__": main()
