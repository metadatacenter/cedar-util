#!/usr/bin/python3

# Utility to filter EBI biosamples based on different criteria

import json
import os

#INPUT_FOLDER = '/Users/marcosmr/tmp/ARM_resources/ebi_biosamples/biosamples_original'
INPUT_FOLDER = '/Users/marcosmr/tmp/ARM_resources/ebi_biosamples/biosamples_filtered_old'
OUTPUT_FOLDER = '/Users/marcosmr/tmp/ARM_resources/ebi_biosamples/biosamples_filtered'

# Enabled filters (note that the filter_is_homo_sapiens is always enabled)
ENABLED_FILTER_NOT_NCBI_SAMPLE = False
ENABLED_FILTER_NOT_GEO_SAMPLE = True
ENABLED_FILTER_IS_ARRAYEXPRESS_SAMPLE = True
ENABLED_FILTER_NOT_ARRAYEXPRESS_SAMPLE = False
ENABLED_FILTER_NOT_ENA_SAMPLE = False
ENABLED_FILTER_HAS_MINIMUM_RELEVANT_ATTRIBUTES_COUNT = True


def filter_is_homo_sapiens(samples):
    """
    Selects homo sapiens samples
    :param samples: An array of samples 
    :return: An array of filtered samples
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


def filter_not_ncbi_sample(samples):
    """
    Selects all samples that are not from the NCBI BioSample database
    :param samples: An array of samples 
    :return: An array of filtered samples
    """
    selected_samples = []
    for sample in samples:
        if 'accession' in sample:
            if not sample['accession'].startswith('SAMN'):
                selected_samples.append(sample)
    return selected_samples


def filter_not_geo_sample(samples):
    """
    Selects all samples that are not from the GEO database
    :param samples: An array of samples 
    :return: An array of filtered samples
    """
    selected_samples = []
    for sample in samples:
        if 'accession' in sample:
            if not sample['name'].startswith('source GSM') and not sample['name'].startswith('source GSE'):
                selected_samples.append(sample)
    return selected_samples


def filter_is_arrayexpress_sample(samples):
    """
      Selects all samples that are from the ArrayExpress database
      :param samples: An array of samples 
      :return: An array of selected samples
      """
    selected_samples = []
    for sample in samples:
        if 'externalReferences' in sample:
            include = True
            for ext in sample['externalReferences']:
                if 'name' in ext:
                    if ext['name'] == 'ArrayExpress':
                        selected_samples.append(sample)
    return selected_samples


def filter_not_arrayexpress_sample(samples):
    """
    Selects all samples that are not from the ArrayExpress database
    :param samples: An array of samples 
    :return: An array of filtered samples
    """
    selected_samples = []
    for sample in samples:
        if 'externalReferences' in sample:
            include = True
            for ext in sample['externalReferences']:
                if 'name' in ext:
                    if ext['name'] == 'ArrayExpress':
                        include = False
            if include:
                selected_samples.append(sample)
    return selected_samples


def filter_not_ena_sample(samples):
    """
    Selects all samples that are not from the European Nucleotide Archive database
    :param samples: An array of samples 
    :return: An array of filtered samples
    """
    selected_samples = []
    for sample in samples:
        if 'externalReferences' in sample:
            include = True
            for ext in sample['externalReferences']:
                if 'name' in ext:
                    if ext['name'] == 'ENA':
                        include = False
            if include:
                selected_samples.append(sample)
    return selected_samples


def filter_has_minimum_relevant_attributes_count(samples, min_count=2):
    """
    Selects all samples that have a minimum number of relevant attributes
    :param samples: An array of samples 
    :param min_count: Minimum number of attributes
    :return: An array of filtered samples
    """
    relevant_att_names = ['sex', 'organismPart', 'cellLine', 'cellType', 'diseaseState', 'ethnicity']
    selected_samples = []
    for sample in samples:
        matches = 0
        if 'characteristics' in sample:
            for ch_name in sample['characteristics'].keys():
                if ch_name in relevant_att_names:
                    matches = matches + 1
            if matches >= min_count:
                selected_samples.append(sample)
    return(selected_samples)


def save_to_files(json_array, output_folder_path, items_per_file, file_base_name):
    """
    Exports an array of json objects to multiple files
    :param json_array: 
    :param output_folder_path: 
    :param items_per_file: 
    :param file_base_name: 
    """
    file_items = []
    start_index = 0
    file_count = 1
    total_items_saved = 0
    for item in json_array:
        file_items.append(item)
        total_items_saved = total_items_saved + 1
        if len(file_items) == items_per_file or total_items_saved == len(json_array):  # Limit reached. Save results
            output_file_path = output_folder_path + '/' + file_base_name \
                               + '_' + str(file_count) + '_' + str(start_index) + 'to' + str(total_items_saved - 1) + '.json'
            # save to file
            with open(output_file_path, 'w') as outfile:
                json.dump(file_items, outfile)
            outfile.close()

            start_index = total_items_saved
            file_count = file_count + 1
            file_items = []


def get_percentage_str(count, total):
    return "%.0f%%" % (100 * count / total)


def apply_remove_filters():
    total_processed = 0
    removed_filter_is_homo_sapiens = 0
    removed_filter_not_ncbi_sample = 0
    removed_filter_not_geo_sample = 0
    removed_filter_is_arrayexpress_sample = 0
    removed_filter_not_arrayexpress_sample = 0
    removed_filter_not_ena_sample = 0
    removed_filter_has_minimum_relevant_attributes_count = 0
    selected_samples = []
    for f in sorted(os.listdir(INPUT_FOLDER)):
        if ".json" in f:  # basic check to be sure that we are processing the right files
            file_path = os.path.join(INPUT_FOLDER, f)
            samples_json = json.load(open(file_path, "r"))
            total_processed = total_processed + len(samples_json)
            print('Processing file: ' + f)

            # Apply filter_is_homo_sapiens
            before_filtering_count = len(samples_json)
            selected_samples_partial = filter_is_homo_sapiens(samples_json)
            removed_count = before_filtering_count - len(selected_samples_partial)
            removed_filter_is_homo_sapiens = removed_filter_is_homo_sapiens + removed_count

            if ENABLED_FILTER_NOT_GEO_SAMPLE:
                # Apply filter_not_geo_sample
                before_filtering_count = len(selected_samples_partial)
                selected_samples_partial = filter_not_geo_sample(selected_samples_partial)
                removed_count = before_filtering_count - len(selected_samples_partial)
                removed_filter_not_geo_sample = removed_filter_not_geo_sample + removed_count

            if ENABLED_FILTER_IS_ARRAYEXPRESS_SAMPLE:
                # Apply filter_is_arrayexpress_sample
                before_filtering_count = len(selected_samples_partial)
                selected_samples_partial = filter_is_arrayexpress_sample(selected_samples_partial)
                removed_count = before_filtering_count - len(selected_samples_partial)
                removed_filter_is_arrayexpress_sample = removed_filter_is_arrayexpress_sample + removed_count

            if ENABLED_FILTER_NOT_ARRAYEXPRESS_SAMPLE:
                # Apply filter_not_arrayexpress_sample
                before_filtering_count = len(selected_samples_partial)
                selected_samples_partial = filter_not_arrayexpress_sample(selected_samples_partial)
                removed_count = before_filtering_count - len(selected_samples_partial)
                removed_filter_not_arrayexpress_sample = removed_filter_not_arrayexpress_sample + removed_count

            if ENABLED_FILTER_NOT_NCBI_SAMPLE:
                # Apply filter_not_ncbi_sample
                before_filtering_count = len(selected_samples_partial)
                selected_samples_partial = filter_not_ncbi_sample(selected_samples_partial)
                removed_count = before_filtering_count - len(selected_samples_partial)
                removed_filter_not_ncbi_sample = removed_filter_not_ncbi_sample + removed_count

            if ENABLED_FILTER_NOT_ENA_SAMPLE:
                # Apply filter_not_ena_sample
                before_filtering_count = len(selected_samples_partial)
                selected_samples_partial = filter_not_ena_sample(selected_samples_partial)
                removed_count = before_filtering_count - len(selected_samples_partial)
                removed_filter_not_ena_sample = removed_filter_not_ena_sample + removed_count

            if ENABLED_FILTER_HAS_MINIMUM_RELEVANT_ATTRIBUTES_COUNT:
                # Apply filter_has_minimum_relevant_attributes_count
                before_filtering_count = len(selected_samples_partial)
                selected_samples_partial = filter_has_minimum_relevant_attributes_count(selected_samples_partial)
                removed_count = before_filtering_count - len(selected_samples_partial)
                removed_filter_has_minimum_relevant_attributes_count = removed_filter_has_minimum_relevant_attributes_count + removed_count

            # Add to list of samples
            selected_samples = selected_samples + selected_samples_partial
            print('Accumulated selected samples: ' + str(len(selected_samples)))

    # Print info
    print('Finished filtering:')
    print('- Initial samples: ' + str(total_processed))
    print('- Removed by filter_is_homo_sapiens: ' + str(removed_filter_is_homo_sapiens) + '(' + get_percentage_str(
        removed_filter_is_homo_sapiens, total_processed) + ')')
    print('- Removed by filter_not_geo_sample: ' + str(removed_filter_not_geo_sample) + '(' + get_percentage_str(
        removed_filter_not_geo_sample, total_processed) + ')')
    print('- Removed by filter_is_arrayexpress_sample: ' + str(
        removed_filter_is_arrayexpress_sample) + '(' + get_percentage_str(
        removed_filter_is_arrayexpress_sample, total_processed) + ')')
    print('- Removed by filter_not_arrayexpress_sample: ' + str(
        removed_filter_not_arrayexpress_sample) + '(' + get_percentage_str(
        removed_filter_not_arrayexpress_sample, total_processed) + ')')
    print('- Removed by filter_not_ncbi_sample: ' + str(removed_filter_not_ncbi_sample) + '(' + get_percentage_str(
        removed_filter_not_ncbi_sample, total_processed) + ')')
    print('- Removed by filter_not_ena_sample: ' + str(
        removed_filter_not_ena_sample) + '(' + get_percentage_str(
        removed_filter_not_ena_sample, total_processed) + ')')
    print('- Removed by filter_has_minimum_relevant_attributes_count: ' + str(
        removed_filter_has_minimum_relevant_attributes_count) + '(' + get_percentage_str(
        removed_filter_has_minimum_relevant_attributes_count, total_processed) + ')')
    print('- Filtered samples: ' + str(len(selected_samples)))
    return selected_samples


def main():
    selected_samples = apply_remove_filters()
    # export to files
    print('Exporting selected samples')
    save_to_files(selected_samples, OUTPUT_FOLDER, 10000, 'ebi_biosamples_filtered')


if __name__ == "__main__": main()
