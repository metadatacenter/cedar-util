#!/usr/bin/python3

# Utility to filter NCBI biosamples based on different criteria. It generates an output XML file with all the
# biosamples selected

import cedar_util
import codecs
import xml.dom.pulldom as pulldom
import xml.etree.ElementTree as ET

# INPUT_FILE = '/Users/marcosmr/tmp/ARM_resources/ncbi_biosample/biosamples_original/2013-03-09-biosample_set.xml'
# OUTPUT_FILE = '/Users/marcosmr/tmp/ARM_resources/ncbi_biosample/biosamples_filtered/biosample_result_filtered.xml'

INPUT_FILE = '/Users/marcosmr/tmp/ARM_resources/ncbi_biosample/biosamples_filtered/homo_sapiens-min_3_attribs/biosample_result_filtered.xml'
OUTPUT_FILE = '/Users/marcosmr/tmp/ARM_resources/ncbi_biosample/biosamples_filtered/homo_sapiens-min_3_attribs_valid/biosample_result_filtered.xml'


def is_homo_sapiens_sample(sample):
    """
    Check if a sample is from homo sapiens
    :param sample: A string containing a biosample in xml format
    :return: Boolean
    """
    biosample_node = ET.fromstring(sample)
    description = biosample_node.find('Description')
    if description is not None:
        organism = description.find('Organism')
        if organism is not None:
            organism_name = organism.get('taxonomy_name')
            if organism_name == 'Homo sapiens':
                return True
    return False


def is_geo_sample(sample):
    """
    Check if a sample is from the GEO database
    :param sample: A string containing a biosample in xml format
    :return: Boolean
    """
    biosample_node = ET.fromstring(sample)
    ids = biosample_node.find('Ids')
    if ids is not None:
        for id in ids:
            db = id.get('db')
            if db == 'GEO':
                return True
    return False


def has_minimum_attributes_count(sample, min_count=3):
    """
    Check if a sample has a minimum number of attributes
    :param sample: A string containing a biosample in xml format
    :param min_count: Minimum number of attributes
    :return: Boolean
    """
    biosample_node = ET.fromstring(sample)
    attributes = biosample_node.find('Attributes')
    if attributes is not None:
        if len(attributes) >= min_count:
            return True
    return False


def has_minimum_relevant_attributes_count(sample, min_count=2):
    """
    Check if a sample has a minimum number of relevant attributes
    :param sample: A string containing a biosample in xml format
    :param min_count: Minimum number of attributes
    :return: Boolean
    """
    relevant_att_names = ['sex', 'tissue', 'disease', 'cell_type', 'cell type' 'cell_line', 'cell line' 'ethnicity',
                          'treatment']
    biosample_node = ET.fromstring(sample)
    attributes = biosample_node.find('Attributes')
    if attributes is not None:
        if len(attributes) >= min_count:
            matches = 0
            for att in attributes:
                attribute_name = att.get('attribute_name')
                display_name = att.get('display_name')
                harmonized_name = att.get('harmonized_name')
                value = None
                if attribute_name in relevant_att_names:
                    value = cedar_util.extract_ncbi_attribute_value(att, attribute_name)
                elif display_name in relevant_att_names:
                    value = cedar_util.extract_ncbi_attribute_value(att, display_name)
                elif harmonized_name in relevant_att_names:
                    value = cedar_util.extract_ncbi_attribute_value(att, harmonized_name)

                # Check if the value is valid
                if value is not None and cedar_util.is_valid_value(value):
                    matches = matches + 1

            if matches >= min_count:
                return True
            else:
                return False
        else:
            return False
    else:
        return False


def main():
    # Read biosamples from XML file
    content = pulldom.parse(INPUT_FILE)
    processed_samples_count = 0
    selected_samples_count = 0
    with codecs.open(OUTPUT_FILE, 'w', 'utf-8') as f:
        f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        f.write("<BioSampleSet>")
        for event, node in content:
            if event == 'START_ELEMENT' and node.tagName == 'BioSample':
                content.expandNode(node)
                node_xml = node.toxml()

                # if is_homo_sapiens_sample(node_xml):
                if has_minimum_relevant_attributes_count(node_xml, 3):
                    f.write('\n' + node.toxml())
                    selected_samples_count = selected_samples_count + 1
                    # Filter: is from GEO
                    # if is_geo_sample(node_xml):
                    #     # Filter: has a minimum number of attributes
                    #     if has_minimum_relevant_attributes_count(node_xml):
                    #         f.write('\n' + node.toxml())
                    #         selected_samples_count = selected_samples_count + 1
                processed_samples_count = processed_samples_count + 1
                if processed_samples_count % 1000 == 0:
                    print('Processed samples: ' + str(processed_samples_count))
                    print('Selected samples: ' + str(selected_samples_count))

        f.write("\n</BioSampleSet>\n")
    f.close()

    print('Finished processing NCBI samples')
    print('- Total samples processed: ' + str(processed_samples_count))
    print('- Total samples selected: ' + str(selected_samples_count))


if __name__ == "__main__": main()
