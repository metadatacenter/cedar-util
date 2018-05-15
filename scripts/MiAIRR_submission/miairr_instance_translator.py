# Utility to translate a MiAIRR instance to the latest version of the template
import json
from pprint import pprint
import copy
import random


OUTPUT_FILE = "new_populated_instance.json"


def generate_value_object(value):
    return {
        '@value': value
    }


def generate_ontology_term_object(uri, label):
    return {
        '@id': uri,
        'rdfs:label': label
    }


def translate_bioproject(source_bioproject, destination_bioproject):
    not_available_term = generate_ontology_term_object(
        'http://data.bioontology.org/provisional_classes/732bcd70-3457-0136-3944-005056010073', 'not available')

    destination_bioproject['Study Criteria'] = source_bioproject['Study Criteria']
    destination_bioproject['Study ID'] = source_bioproject['Study ID']
    destination_bioproject['Funding Agency'] = source_bioproject['Funding Agency']
    destination_bioproject['Lab Name'] = source_bioproject['Lab Name']
    destination_bioproject['Study Title'] = source_bioproject['Study Title']
    destination_bioproject['Study Type'] = not_available_term
    destination_bioproject['Relevant Publications'] = source_bioproject['Relevant Publication']
    destination_bioproject['Lab Address'] = source_bioproject['Department']
    destination_bioproject['Contact Information (data collection)'] = source_bioproject[
        'Contact Information (Corresponding author e-mail)']
    return destination_bioproject


def translate_biosample(source_biosample, destination_biosample, suffix):

    not_available_term = generate_ontology_term_object(
        'http://data.bioontology.org/provisional_classes/732bcd70-3457-0136-3944-005056010073', 'not available')

    # Subject
    destination_biosample['Subject ID'] = source_biosample['Subject id']
    destination_biosample['Synthetic Library'] = generate_value_object(None)
    destination_biosample['Organism'] = source_biosample['Organism']
    source_sex = source_biosample['Sex']['@value']
    if source_sex == 'male':
        destination_biosample['Sex'] = generate_ontology_term_object(
            'http://purl.bioontology.org/ontology/SNOMEDCT/248153007', 'Male')
    elif source_sex == 'female':
        destination_biosample['Sex'] = generate_ontology_term_object(
            'http://purl.bioontology.org/ontology/SNOMEDCT/248152002', 'Female')
    else:
        destination_biosample['Sex'] = not_available_term

    destination_biosample['Age'] = source_biosample['Age']
    destination_biosample['Age Event'] = source_biosample['Age Event']
    destination_biosample['Ancestry Population'] = source_biosample['Ancestry Population']
    destination_biosample['Ethnicity'] = source_biosample['Ethnicity']
    destination_biosample['Race'] = source_biosample['Race']
    destination_biosample['Strain Name'] = source_biosample['Strain Name']
    destination_biosample['Related Subjects'] = source_biosample['Relation to other Subject']
    destination_biosample['Relation Type'] = source_biosample['Relation Type']
    destination_biosample['Projected Release Date'] = source_biosample[
        'Projected Release Date']  # TODO: format conversion
    # Diagnosis
    destination_biosample['Study Group Description'] = source_biosample['Study Group Description']
    destination_biosample['Diagnosis1'] = not_available_term
    destination_biosample['Length of Disease'] = source_biosample['Length of Disease']
    destination_biosample['Disease Stage'] = source_biosample['Disease stage']
    destination_biosample['Prior Therapies for Primary Disease under Study'] = source_biosample[
        'Prior Therapies for Primary Disease under Study']
    destination_biosample['Immunogen'] = source_biosample['Immunogen']
    destination_biosample['Intervention Definition'] = source_biosample['Intervention Definition']
    destination_biosample['Other Relevant Medical History'] = source_biosample['Other Relevant Medical History']
    # Biological Sample
    destination_biosample['Sample ID'] = source_biosample['Sample name']
    destination_biosample['Sample ID']['@value'] = destination_biosample['Sample ID']['@value'] + '_' + suffix

    destination_biosample['Sample Type'] = source_biosample['Sample Type']
    destination_biosample['Tissue'] = source_biosample['Tissue']
    destination_biosample['Anatomic Site'] = source_biosample['Anatomic Site']
    destination_biosample['Disease State of Sample'] = source_biosample['Disease State of Sample']
    destination_biosample['Sample Collection Time'] = source_biosample['Sample Collection Time']
    destination_biosample['Collection Time Event'] = source_biosample['Collection Time Event T0']
    destination_biosample['Biomaterial Provider'] = source_biosample['Biomaterial Provider']
    # Processing
    destination_biosample['Tissue Processing'] = source_biosample['Tissue Processing']
    destination_biosample['Cell Subset'] = source_biosample['Cell Subset']
    destination_biosample['Cell Subset Phenotype'] = source_biosample['Cell Subset Phenotype']
    destination_biosample['Single-cell Sort'] = source_biosample['Single-cell Sort']
    destination_biosample['Number of Cells in Experiment'] = source_biosample['Number of Cells in Experiment']
    destination_biosample['Number of Cells per Sequencing Reaction'] = source_biosample[
        'Number of Cells per Sequencing Reaction']
    destination_biosample['Cell Storage'] = source_biosample['Cell Storage']
    destination_biosample['Cell Quality'] = source_biosample['Cell Quality']
    destination_biosample['Cell Isolation'] = source_biosample['Cell Isolation']
    destination_biosample['Cell Processing Protocol'] = source_biosample['Processing Protocol']
    # optional attributes
    optional_attributes = source_biosample['Optional Attribute']
    destination_biosample['Optional BioSample Attribute'] = optional_attributes
    for op in optional_attributes:
        destination_biosample[op] = source_biosample[op]

    return destination_biosample


def translate_sra(source_sra, destination_sra, suffix):
    not_available_value = generate_value_object('NA')

    destination_sra['Sample ID'] = source_sra['Sample Name']
    destination_sra['Sample ID']['@value'] = source_sra['Sample Name']['@value'] + '_' + suffix
    destination_sra['Target Substrate'] = source_sra['Target Substrate']
    destination_sra['Target Substrate Quality'] = source_sra['Target Substrate Quality']
    destination_sra['Template Amount'] = source_sra['Template Amount']
    destination_sra['Nucleic Acid Processing ID'] = not_available_value
    destination_sra['Library Generation Method'] = source_sra['Library Generation Method']
    destination_sra['Library Generation Protocol'] = source_sra['Library Generation Protocol']
    destination_sra['Protocol IDs'] = source_sra['Protocol ID']
    destination_sra['Target Locus for PCR'] = source_sra['Target Locus for PCR']
    destination_sra['Forward PCR Primer Target Location'] = source_sra['Forward PCR Primer Target Location']
    destination_sra['Reverse PCR Primer Target Location'] = source_sra['Reverse PCR Primer Target Location']
    destination_sra['Complete Sequences'] = source_sra['Complete Sequence']
    destination_sra['Physical Linkage of Different Loci'] = source_sra['Physical Linkage of Different Loci']
    destination_sra['Total Reads Passing QC Filter'] = source_sra['Total Reads Passing QC Filter']
    destination_sra['Sequencing Platform'] = source_sra['Sequencing Platform']
    destination_sra['Read Lengths'] = source_sra['Read Lengths']
    destination_sra['Sequencing Facility'] = source_sra['Sequencing Facility']
    destination_sra['Batch Number'] = source_sra['Batch Number']
    destination_sra['Date of Sequencing Run'] = source_sra['Date of Sequencing Run']
    destination_sra['Sequencing Kit'] = source_sra['Sequencing Kit']
    destination_sra['File Type'] = source_sra['File Type']
    # optional attributes
    file_names = source_sra['filename']
    destination_sra['filename'] = file_names
    for file_name in file_names:
        destination_sra[file_name] = source_sra[file_name]

    return destination_sra


def main():

    with open("source_instance.json", encoding='utf-8') as f:
        source_instance = json.load(f)

    with open("new_empty_instance.json", encoding='utf-8') as f:
        dest_instance = json.load(f)


    # random suffix used to generate different sample ids each time
    suffix = str(random.randint(0, 999999999))

    # BioProject
    source_bioproject = source_instance['BioProject']
    dest_bioproject = dest_instance['BioProject for AIRR NCBI']
    final_bioproject = translate_bioproject(source_bioproject, copy.copy(dest_bioproject))

    # BioSample
    source_biosamples = source_instance['BioSample']
    dest_biosample = dest_instance['BioSample for AIRR NCBI'][0]
    final_biosamples = []
    for source_biosample in source_biosamples:
        final_biosamples.append(translate_biosample(source_biosample, copy.copy(dest_biosample), suffix))

    # SRA
    source_sras = source_instance['Sequence Read Archive']
    dest_sra = dest_instance['Sequence Read Archive for AIRR NCBI'][0]
    final_sras = []
    for source_sra in source_sras:
        final_sras.append(translate_sra(source_sra, copy.copy(dest_sra), suffix))

    dest_instance['BioProject for AIRR NCBI'] = final_bioproject
    dest_instance['BioSample for AIRR NCBI'] = final_biosamples
    dest_instance['Sequence Read Archive for AIRR NCBI'] = final_sras

    with open(OUTPUT_FILE, 'w') as outfile:
        json.dump(dest_instance, outfile)


if __name__ == "__main__": main()
