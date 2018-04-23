#!/usr/bin/python3

# Utility to annotate keywords using the NCBO Annotator

import json
import time
import os
import sys
import term_normalizer
import bioportal_util
import annotation_constants

# INPUT
UNIQUE_VALUES_FILE_PATH = annotation_constants.VALUES_ANNOTATION_INPUT_VALUES_FILE_PATH

# OUTPUT
UNIQUE_VALUES_ANNOTATED_FILE_PATH_1 = annotation_constants.VALUES_ANNOTATION_OUTPUT_FILE_PATH_1
UNIQUE_VALUES_ANNOTATED_FILE_PATH_2 = annotation_constants.VALUES_ANNOTATION_OUTPUT_FILE_PATH_2
MAPPINGS_FILE_PATH_1 = annotation_constants.VALUES_ANNOTATION_MAPPINGS_FILE_PATH_1
MAPPINGS_FILE_PATH_2 = annotation_constants.VALUES_ANNOTATION_MAPPINGS_FILE_PATH_2

# OTHER SETTINGS
BIOPORTAL_API_KEY = annotation_constants.VALUES_ANNOTATION_BIOPORTAL_API_KEY
VALUES_PER_ITERATION = annotation_constants.VALUES_ANNOTATION_VALUES_PER_ITERATION
# List of relevant ontologies. The algorithm will try to pick pref_class_label and pref_class_uri from one of these
# ontologies. If that's not possible, it will pick values from any other ontologies
PREFERRED_ONTOLOGIES_1 = annotation_constants.VALUES_ANNOTATION_PREFERRED_ONTOLOGIES_1
PREFERRED_ONTOLOGIES_2 = annotation_constants.VALUES_ANNOTATION_PREFERRED_ONTOLOGIES_2
USE_NORMALIZED_VALUES = annotation_constants.VALUES_ANNOTATION_USE_NORMALIZED_VALUES
NORMALIZED_VALUES_FILE_NAME = annotation_constants.VALUES_ANNOTATION_NORMALIZED_VALUES_FILE_NAME  # We assume that the file is stored in the current path
LIMIT_ANNOTATOR_TO_PREFERRED_ONTOLOGIES = annotation_constants.VALUES_ANNOTATION_LIMIT_TO_PREFERRED_ONTOLOGIES


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


def ontology_has_more_priority(ont1, ont2, preferred_ontologies):
    """
    Checks if ont1 has more priority than ont2 according to a defined list of priorities
    :param ont1: 
    :param ont2: 
    :param preferred_ontologies: 
    :return: 
    """
    if ont1 in preferred_ontologies:
        if ont2 in preferred_ontologies:
            if preferred_ontologies.index(ont1) < preferred_ontologies.index(ont2):
                return True
        else:
            return True
    else:
        return False


def extract_keyword_annotations(keywords, annotations, preferred_ontologies):
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
                        if ontology_has_more_priority(class_ontology_id, keyword_annotation.pref_class_ontology, preferred_ontologies):
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


def generate_mappings(unique_values_annotated):
    """
    Using the generated annotations it generates a file with mappings from all preferred URIS found in the annotations to any other equivalent URIS
    """
    mappings = {}
    count = 0
    for value in unique_values_annotated:
        pref_uri = unique_values_annotated[value]['pref_class_uri']
        equivalent_uris = unique_values_annotated[value]['class_uris']

        if pref_uri not in mappings:
            mappings[pref_uri] = []

        for equivalent_uri in equivalent_uris:
            if equivalent_uri not in mappings[pref_uri] and equivalent_uri != pref_uri:
                mappings[pref_uri].append(equivalent_uri)

        count = count + 1
    print('No. values processed: ' + str(count) + "/" + str(len(unique_values_annotated)))
    print('Total no. of uri keys in file: ' + str(len(mappings)))
    return mappings


#     uris_annotated = {}
#     for value in unique_values_annotated:
#         uri = unique_values_annotated[value]['pref_class_uri']
#         uris_annotated[uri] = unique_values_annotated[value]


def main():
    # Read unique values
    with open(UNIQUE_VALUES_FILE_PATH) as f:
        all_values = f.read().splitlines()

    # Test data
    # all_values = ['m', 'male']
    # all_values = ['peripheral blood']
    # all_values = ['organism part']

    # Load file with normalized values
    if USE_NORMALIZED_VALUES:
        norm_values = json.loads(open(os.path.join(sys.path[0], NORMALIZED_VALUES_FILE_NAME)).read())
    else:
        norm_values = None

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

    unique_values_annotated_1 = {}
    unique_values_annotated_2 = {}

    total_count = 0
    print('Annotation process started...')

    for keywords_list in input_keywords_lists:

        time.sleep(.150)  # wait between calls to the Annotator

        ontologies = []
        if LIMIT_ANNOTATOR_TO_PREFERRED_ONTOLOGIES:
            ontologies = PREFERRED_ONTOLOGIES_1

        annotations = bioportal_util.annotate(BIOPORTAL_API_KEY, ",".join(keywords_list), ontologies, longest_only=True,
                                              expand_mappings=True, include=['prefLabel'])

        # Extract annotations using PREFERRED_ONTOLOGIES_1
        keyword_annotations_1 = extract_keyword_annotations(keywords_list, annotations, PREFERRED_ONTOLOGIES_1)
        for ann in keyword_annotations_1:
            annotation_key = ann.keyword

            if annotation_key not in unique_values_annotated_1:
                unique_values_annotated_1[annotation_key] = KeywordAnnotation.obj_dict(ann)
            else:
                print('Keyword already there: ' + annotation_key)

        # Extract annotations using PREFERRED_ONTOLOGIES_2
        keyword_annotations_2 = extract_keyword_annotations(keywords_list, annotations, PREFERRED_ONTOLOGIES_2)
        for ann in keyword_annotations_2:
            annotation_key = ann.keyword

            if annotation_key not in unique_values_annotated_2:
                unique_values_annotated_2[annotation_key] = KeywordAnnotation.obj_dict(ann)
            else:
                print('Keyword already there: ' + annotation_key)

        total_count = total_count + 1
        print('Total lists of keywords processed: ' + str(total_count) + '/' + str(len(input_keywords_lists)))

    # Write to files
    with open(UNIQUE_VALUES_ANNOTATED_FILE_PATH_1, 'w') as outfile:
        json.dump(unique_values_annotated_1, outfile)
    with open(UNIQUE_VALUES_ANNOTATED_FILE_PATH_2, 'w') as outfile:
        json.dump(unique_values_annotated_2, outfile)

    # Generate mappings and write them to file
    mappings_1 = generate_mappings(unique_values_annotated_1)
    with open(MAPPINGS_FILE_PATH_1, 'w') as outfile:
        json.dump(mappings_1, outfile)
    mappings_2 = generate_mappings(unique_values_annotated_2)
    with open(MAPPINGS_FILE_PATH_2, 'w') as outfile:
        json.dump(mappings_2, outfile)


# #used to generate the mappings from the annotations file without regenerating the annotations file
# def main2():
#     unique_values_annotated = json.load(open(UNIQUE_VALUES_ANNOTATED_FILE_PATH))
#     # Generate mappings and write them to file
#     mappings = generate_mappings(unique_values_annotated)
#     with open(MAPPINGS_FILE_PATH, 'w') as outfile:
#         json.dump(mappings, outfile)


if __name__ == "__main__": main()
