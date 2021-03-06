# Utility to translate a MiAIRR instance to the latest version of the template
import json
from pprint import pprint
import copy
import random

OUTPUT_FILE = "new_populated_instance.json"
# If we use Star Wars identifiers (Chewbacca, Hans Solo, etc.) the NCBI team knows that a submission is a test
# submission, and won't worry about it being approved/in the system
USE_STAR_WARS_DATA = True
CONTACT_EMAIL = "marcosmr@stanford.edu" # Only used when using STAR WARS data
STAR_WARS_PREFIX = 'STARWARS_'
MY_BIOPROJECT_ID = 'PRJNA471695'
SUBMISSIONS_RELEASE_DATE = '2023-07-07'
APPEND_SUFFIX_TO_IDS = True # random suffix used to generate different sample ids each time


def generate_value_object(value):
    return {
        '@value': value
    }


def generate_ontology_term_object(uri, label):
    return {
        '@id': uri,
        'rdfs:label': label
    }


# replaces a subjectId with a new generated one, to avoid duplication
def replace_subject_id(json_data, subject_id, new_subject_id):
    for field in json_data:
        if json_data[field] and '@value' in json_data[field] and json_data[field][
            '@value'] is not None and subject_id in json_data[field]['@value']:
            json_data[field]['@value'] = json_data[field]['@value'].replace(subject_id, new_subject_id)

    return json_data


def translate_bioproject(source_bioproject, destination_bioproject, contact_email):
    not_available_term = generate_ontology_term_object(
        'http://data.bioontology.org/provisional_classes/732bcd70-3457-0136-3944-005056010073', 'not available')

    if USE_STAR_WARS_DATA:
        destination_bioproject['Study Criteria']['@value'] = \
            'Jedis were diagnosed according to the Dark Side criteria'
        destination_bioproject['Funding Agency']['@value'] = 'The Force'
        destination_bioproject['Lab Address']['@value'] = 'Department of the Universe'
        destination_bioproject['Lab Name']['@value'] = 'Jedi Lab'
        destination_bioproject['Study Title']['@value'] = \
            'The Star Wars study: An analysis of cell types in Jedis'
        destination_bioproject['Contact Information (data collection)']['@value'] = contact_email
    else:
        destination_bioproject['Study Criteria'] = source_bioproject['Study Criteria']
        destination_bioproject['Funding Agency'] = source_bioproject['Funding Agency']
        destination_bioproject['Lab Address'] = source_bioproject['Department']
        destination_bioproject['Lab Name'] = source_bioproject['Lab Name']
        destination_bioproject['Study Title'] = source_bioproject['Study Title']
        destination_bioproject['Contact Information (data collection)']['@value'] = source_bioproject['E-mail']['@value']

    bioproject_id = source_bioproject['Study ID']['@value']

    if USE_STAR_WARS_DATA:
        destination_bioproject['Study ID']['@value'] = MY_BIOPROJECT_ID
    else:
        destination_bioproject['Study ID']['@value'] = bioproject_id

    destination_bioproject['Relevant Publications'] = source_bioproject['Relevant Publication']
    destination_bioproject['Study Type'] = not_available_term

    # destination_bioproject['Contact Information (data collection)'] = source_bioproject[
    #     'Contact Information (Corresponding author e-mail)']

    return destination_bioproject


def translate_biosample(source_biosample, destination_biosample, suffix):
    not_available_term = generate_ontology_term_object(
        'http://data.bioontology.org/provisional_classes/732bcd70-3457-0136-3944-005056010073', 'not available')

    subject_id = source_biosample['Subject id']['@value']
    if USE_STAR_WARS_DATA:
        new_subject_id = STAR_WARS_PREFIX + subject_id + suffix
    else:
        new_subject_id = subject_id + suffix

    # Subject
    destination_biosample['Subject ID'] = source_biosample['Subject id']
    destination_biosample['Synthetic Library'] = [generate_value_object(None)]
    destination_biosample['Organism'] = source_biosample['Organism']
    #source_sex = source_biosample['Sex']['@value']
    # if source_sex == 'male':
    #     destination_biosample['Sex'] = generate_ontology_term_object(
    #         'http://purl.bioontology.org/ontology/SNOMEDCT/248153007', 'Male')
    # elif source_sex == 'female':
    #     destination_biosample['Sex'] = generate_ontology_term_object(
    #         'http://purl.bioontology.org/ontology/SNOMEDCT/248152002', 'Female')
    # else:
    #     destination_biosample['Sex'] = not_available_term
    destination_biosample['Sex'] = source_biosample['Sex']

    destination_biosample['Age'] = source_biosample['Age']
    destination_biosample['Age Event'] = source_biosample['Age Event']
    destination_biosample['Ancestry Population'] = source_biosample['Ancestry Population']
    destination_biosample['Ethnicity'] = source_biosample['Ethnicity']
    destination_biosample['Race'] = source_biosample['Race']
    destination_biosample['Strain Name'] = source_biosample['Strain Name']
    destination_biosample['Relation to Other Subjects'] = source_biosample['Relation to other Subject']
    destination_biosample['Relation Type'] = source_biosample['Relation Type']
    destination_biosample['Estimated Release Date'] = source_biosample['Projected Release Date']  # TODO: format conversion
    # Diagnosis
    if USE_STAR_WARS_DATA:
        destination_biosample['Study Group Description']['@value'] = 'Cells from Jedis'
    else:
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
    destination_biosample['Sample Type'] = source_biosample['Sample Type']
    destination_biosample['Tissue'] = source_biosample['Tissue']
    destination_biosample['Anatomic Site'] = source_biosample['Anatomic Site']
    destination_biosample['Disease State of Sample'] = source_biosample['Disease State of Sample']
    destination_biosample['Sample Collection Time'] = source_biosample['Sample Collection Time']
    destination_biosample['Collection Time Event'] = source_biosample['Collection Time Event T0']
    if USE_STAR_WARS_DATA:
        destination_biosample['Biomaterial Provider']['@value'] = 'Galaxy Provider'
    else:
        destination_biosample['Biomaterial Provider'] = source_biosample['Biomaterial Provider']

    # Processing
    if USE_STAR_WARS_DATA:
        destination_biosample['Tissue Processing']['@value'] = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus maximus et leo quis pretium. Cras quis dolor tellus. Fusce pellentesque sagittis ipsum, at cursus mauris commodo in. Etiam dictum elementum arcu. Pellentesque mattis mollis ultricies. Aliquam pellentesque arcu sit amet odio convallis fermentum. Proin blandit urna leo, non aliquam erat pellentesque ut. Aenean volutpat at lectus a cursus. Sed maximus nunc eu porta posuere. Nam et tellus et turpis efficitur iaculis. Maecenas varius sit amet leo at aliquet. Donec sagittis turpis quam, dapibus vestibulum justo lacinia at. Fusce volutpat sollicitudin dui, in malesuada nisi venenatis et. In eleifend ultrices volutpat.'
        destination_biosample['Processing Protocol']['@value'] = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus maximus et leo quis pretium. Cras quis dolor tellus. Fusce pellentesque sagittis ipsum, at cursus mauris commodo in. Etiam dictum elementum arcu. Pellentesque mattis mollis ultricies. Aliquam pellentesque arcu sit amet odio convallis fermentum. Proin blandit urna leo, non aliquam erat pellentesque ut. Aenean volutpat at lectus a cursus. Sed maximus nunc eu porta posuere. Nam et tellus et turpis efficitur iaculis. Maecenas varius sit amet leo at aliquet. Donec sagittis turpis quam, dapibus vestibulum justo lacinia at. Fusce volutpat sollicitudin dui, in malesuada nisi venenatis et. In eleifend ultrices volutpat.'
    else:
        destination_biosample['Tissue Processing'] = source_biosample['Tissue Processing']
        destination_biosample['Processing Protocol'] = source_biosample['Processing Protocol']

    destination_biosample['Cell Subset'] = source_biosample['Cell Subset']
    destination_biosample['Cell Subset Phenotype'] = source_biosample['Cell Subset Phenotype']
    destination_biosample['Single-cell Sort'] = source_biosample['Single-cell Sort']
    destination_biosample['Number of Cells in Experiment'] = source_biosample['Number of Cells in Experiment']
    destination_biosample['Number of Cells per Sequencing Reaction']['@value'] = source_biosample[
        'Number of Cells per Sequencing Reaction']['@value']
    destination_biosample['Cell Storage'] = source_biosample['Cell Storage']
    destination_biosample['Cell Quality'] = source_biosample['Cell Quality']
    destination_biosample['Cell Isolation'] = source_biosample['Cell Isolation']

    # optional attributes
    optional_attributes = source_biosample['Optional Attribute']
    destination_biosample['Optional BioSample Attribute'] = optional_attributes
    for op in optional_attributes:
        destination_biosample[op] = source_biosample[op]

    # Replace the subjectId with the new subjectId everywhere
    destination_biosample = replace_subject_id(destination_biosample, subject_id, new_subject_id)

    return destination_biosample


def translate_sra(source_sra, destination_sra, suffix):
    not_available_value = generate_value_object('NA')

    sample_id = source_sra['Sample Name']['@value']

    if USE_STAR_WARS_DATA:
        sample_id = STAR_WARS_PREFIX + sample_id

    index = sample_id.find('_')
    if index > 0:
        subject_id = sample_id[:index]
        new_sample_id = subject_id + suffix + sample_id[index:]
        destination_sra['Sample ID']['@value'] = new_sample_id
    else:
        destination_sra['Sample ID']['@value'] = sample_id

    if USE_STAR_WARS_DATA:
        destination_sra['Library Generation Protocol']['@value'] = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla fermentum, metus nec viverra suscipit, sem nunc commodo risus, in mollis eros justo in sem. Morbi eget maximus nunc, sed luctus nisi. Proin sit amet ultrices libero. Nulla auctor at urna at pretium. Aenean vestibulum elit dui, nec blandit lectus tincidunt vel. Curabitur nibh nunc, varius sed odio eget, ornare commodo tellus. Nunc pulvinar justo diam, sed dictum neque condimentum ac. Integer at nisl eget lorem iaculis interdum. Nullam eget lorem eu magna malesuada tincidunt. Nulla et sem malesuada sapien vehicula laoreet ut nec ipsum. Vestibulum ipsum leo, sagittis vitae finibus vitae, volutpat non ligula. Nunc quis eros vitae lorem feugiat porta quis eu lorem.'
        destination_sra['Sequencing Facility']['@value'] = 'Sequencing Facility from the Galaxy'
    else:
        destination_sra['Library Generation Protocol'] = source_sra['Library Generation Protocol']
        destination_sra['Sequencing Facility'] = source_sra['Sequencing Facility']

    destination_sra['Target Substrate'] = source_sra['Target Substrate']
    destination_sra['Target Substrate Quality'] = source_sra['Target Substrate Quality']
    destination_sra['Template Amount'] = source_sra['Template Amount']
    destination_sra['Nucleic Acid Processing ID'] = not_available_value
    destination_sra['Library Strategy'] = source_sra['Library Strategy']
    destination_sra['Library Source'] = source_sra['Library Source']
    destination_sra['Library Selection'] = source_sra['Library Selection']
    destination_sra['Library Layout'] = source_sra['Library Layout']
    destination_sra['Library Generation Method'] = source_sra['Library Generation Method']
    destination_sra['Protocol IDs'] = source_sra['Protocol ID']
    destination_sra['Target Locus for PCR'] = source_sra['Target Locus for PCR']
    destination_sra['Forward PCR Primer Target Location'] = source_sra['Forward PCR Primer Target Location']
    destination_sra['Reverse PCR Primer Target Location'] = source_sra['Reverse PCR Primer Target Location']
    destination_sra['Complete Sequences'] = source_sra['Complete Sequence']
    destination_sra['Physical Linkage of Different Loci'] = source_sra['Physical Linkage of Different Loci']
    destination_sra['Total Reads Passing QC Filter'] = source_sra['Total Reads Passing QC Filter']
    destination_sra['Sequencing Platform'] = source_sra['Sequencing Platform']
    destination_sra['Read Lengths'] = source_sra['Read Lengths']
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

    if APPEND_SUFFIX_TO_IDS:
        # random suffix used to generate different sample ids each time
        suffix = str(random.randint(0, 99999))
    else:
        suffix = ''

    # BioProject
    source_bioproject = source_instance['BioProject']
    dest_bioproject = dest_instance['BioProject for AIRR NCBI']
    final_bioproject = translate_bioproject(source_bioproject, copy.copy(dest_bioproject), CONTACT_EMAIL)

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

    # Set the release date
    if USE_STAR_WARS_DATA:
        dest_instance['Submissions Release Date'] = generate_value_object(SUBMISSIONS_RELEASE_DATE) #TODO add "@type": "xsd:date"
    else:
        dest_instance['Submissions Release Date'] = source_instance['Submissions Release Date']

    dest_instance['BioProject for AIRR NCBI'] = final_bioproject
    dest_instance['BioSample for AIRR NCBI'] = final_biosamples
    dest_instance['Sequence Read Archive for AIRR NCBI'] = final_sras

    with open(OUTPUT_FILE, 'w') as outfile:
        json.dump(dest_instance, outfile)


if __name__ == "__main__": main()
