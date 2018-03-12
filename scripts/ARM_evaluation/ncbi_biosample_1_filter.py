#!/usr/bin/python3

# Utility to filter NCBI biosamples based on different criteria. It generates an output XML file with all the
# biosamples selected

import codecs
import xml.dom.pulldom as pulldom
import xml.etree.ElementTree as ET

INPUT_FILE = '/Users/marcosmr/tmp/ARM_resources/ncbi_biosample/biosamples_original/2013-03-09-biosample_set.xml'
OUTPUT_FILE = '/Users/marcosmr/tmp/ARM_resources/ncbi_biosample/biosamples_filtered/biosample_result_filtered.xml'


def filter_is_geo_samples(samples):
    """
    Selects samples from the GEO database
    :param samples: An array of samples 
    :return: An array of GEO samples
    """
    selected_samples = []
    for sample in samples:
        if 'characteristics' in sample:
            if 'organism' in sample['characteristics']:
                organisms = sample['characteristics']['organism']
                for org in organisms:
                    if 'text' in org and org['text'] == 'Homo sapiens':
                        selected_samples.append(sample)

    return selected_samples


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
                # Filter: is homo sapiens
                if is_homo_sapiens_sample(node_xml):
                    # Filter: is from GEO
                    if is_geo_sample(node_xml):
                        # Filter: has a minimum number of attributes
                        if has_minimum_attributes_count(node_xml, 3):
                            f.write('\n' + node.toxml())
                            selected_samples_count = selected_samples_count + 1
                processed_samples_count = processed_samples_count + 1
                if processed_samples_count % 10000 == 0:
                    print('Processed samples: ' + str(processed_samples_count))
                    print('Selected samples: ' + str(selected_samples_count))

        f.write("\n</BioSampleSet>\n")
    f.close()

    print('Finished processing NCBI samples')
    print('- Total samples processed: ' + str(processed_samples_count))
    print('- Total samples selected: ' + str(selected_samples_count))


if __name__ == "__main__": main()
