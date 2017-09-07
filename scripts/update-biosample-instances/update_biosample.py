#!/usr/bin/python

# Created:      Aug-9-2017
# Last updated: Aug-31-2017
# update_biosample.py: Utility to update all BioSample instances in a local folder to the CEDAR schema version 1.1.0
# and upload them to the CEDAR system

import time
import cedar_util
import json
from collections import OrderedDict

# CONSTANTS DEFINITION
INPUT_PATH = "/Users/marcosmr/Desktop/tmp/annotated"
OUTPUT_PATH = "/Users/marcosmr/Desktop/tmp/annotated_updated"
EMPTY_INSTANCE_PATH = "/Users/marcosmr/Development/git_repos/CEDAR/cedar-util/scripts/update-biosample-instances/empty_instance.json"

# Values of instance fields. The @id will be automatically generated by the target CEDAR system
SCHEMA_IS_BASED_ON = "https://repo.metadatacenter.orgx/templates/ae1d8f8f-fa1f-41e3-89cb-87a69b22add7"  # It must exist in the target system
PAV_CREATED_ON = "2017-08-31T20:54:50-0700"
PAV_CREATED_BY = "https://metadatacenter.org/users/8d787b98-33dd-4aff-a88c-440caf452c61"  # It must exist in the target system
PAV_LAST_UPDATED_ON = "2017-08-31T20:54:50-0700"
OSLC_MODIFIED_BY = "https://metadatacenter.org/users/8d787b98-33dd-4aff-a88c-440caf452c61"  # It must exist in the target system

CONTEXT_FIELD = "@context"
ID_FIELD = "@id"
VALUE_FIELD = "@value"
TYPE_FIELD = "@type"
VALUE_LABEL_FIELD_OLD = "_valueLabel"
VALUE_LABEL_FIELD_NEW = "rdfs:label"

SAMPLE_NAME_FIELD = "sampleName"
ORGANISM_FIELD = "organism"
TISSUE_FIELD = "tissue"
SEX_FIELD = "sex"
ISOLATE_FIELD = "isolate"
AGE_FIELD = "age"
BIOMATERIAL_PROVIDER_FIELD = "biomaterialProvider"
OPTIONAL_ATT_FIELD = "optionalAttribute"
OPTIONAL_ATT_NAME_FIELD = "name"
OPTIONAL_ATT_VALUE_FIELD = "value"
SORT_ORDER = [CONTEXT_FIELD, SAMPLE_NAME_FIELD, ORGANISM_FIELD,
              TISSUE_FIELD, SEX_FIELD, AGE_FIELD, ISOLATE_FIELD, BIOMATERIAL_PROVIDER_FIELD, OPTIONAL_ATT_FIELD,
              PAV_CREATED_ON, PAV_CREATED_BY, PAV_LAST_UPDATED_ON, OSLC_MODIFIED_BY, SCHEMA_IS_BASED_ON]

# Upload destination
SERVER = "https://resource.metadatacenter.orgx/"
FOLDER_ID = "https://repo.metadatacenter.orgx/folders/c05cc17c-4608-4f07-b382-e9521c9e4c55"
API_KEY = "<apiKey>"

OPTIONAL_ATT_CONTEXT = {
    "pav": "http://purl.org/pav/",
    "oslc": "http://open-services.net/ns/core#",
    "name": "https://schema.metadatacenter.orgx/properties/name",
    "value": "https://schema.metadatacenter.orgx/properties/value"
}


def main():
    start_time = time.time()

    # Read instances from local folder
    print('Loading instances...')
    instance_paths = cedar_util.load_json_file_paths_from_folder(INPUT_PATH)

    count = 1;
    total_count = len(instance_paths)
    for instance_path in instance_paths:
        with open(instance_path) as data_file:
            try:
                instance_json = json.load(data_file)
                updated_instance = generate_updated_instance(EMPTY_INSTANCE_PATH, instance_json)
                # Save the updated instance to disk
                with open(OUTPUT_PATH + '/BioSample_instance' + str(count) + '.json', 'w') as outfile:
                    json.dump(updated_instance, outfile)

                # print(json.dumps(updated_instance))

                # Upload instance to the CEDAR system
                try:
                    cedar_util.post_instance(updated_instance, SERVER, SCHEMA_IS_BASED_ON, FOLDER_ID, API_KEY)
                    print("Posted instance no. " + str(count) + " (" + str(float((100 * count) / total_count)) + "%)")
                    count += 1
                except ValueError:
                    print('Error posting instance')

            except ValueError:
                print('Error processing instance')

    print("\nExecution time:  %s seconds " % (time.time() - start_time))


# Populates the empty instance with the values from the old instance and returns it
def generate_updated_instance(empty_instance_path, old_instance):
    # Read empty instance
    instance = cedar_util.load_json_file(empty_instance_path)

    # Populate provenance fields
    instance['schema:isBasedOn'] = SCHEMA_IS_BASED_ON
    instance['pav:createdOn'] = PAV_CREATED_ON
    instance['pav:createdBy'] = PAV_CREATED_BY
    instance['pav:lastUpdatedOn'] = PAV_LAST_UPDATED_ON
    instance['oslc:modifiedBy'] = OSLC_MODIFIED_BY

    # Populate the rest of the fields using the values from the old instance
    # controlled fields
    instance = update_instance_field_not_controlled(SAMPLE_NAME_FIELD, old_instance, instance)
    instance = update_instance_field_not_controlled(ISOLATE_FIELD, old_instance, instance)
    instance = update_instance_field_not_controlled(AGE_FIELD, old_instance, instance)
    instance = update_instance_field_not_controlled(BIOMATERIAL_PROVIDER_FIELD, old_instance, instance)
    # non-controlled fields
    instance = update_instance_field_controlled(ORGANISM_FIELD, old_instance, instance)
    instance = update_instance_field_controlled(TISSUE_FIELD, old_instance, instance)
    instance = update_instance_field_controlled(SEX_FIELD, old_instance, instance)
    # optional attribute element
    if OPTIONAL_ATT_FIELD in old_instance:
        for att in old_instance[OPTIONAL_ATT_FIELD]:
            if OPTIONAL_ATT_NAME_FIELD in att and OPTIONAL_ATT_VALUE_FIELD in att:
                new_optional_att = {CONTEXT_FIELD: OPTIONAL_ATT_CONTEXT, OPTIONAL_ATT_NAME_FIELD: {},
                                    OPTIONAL_ATT_VALUE_FIELD: {}}
                # Optional attribute name
                if VALUE_LABEL_FIELD_OLD in att[OPTIONAL_ATT_NAME_FIELD]:
                    new_optional_att[OPTIONAL_ATT_NAME_FIELD][ID_FIELD] = att[OPTIONAL_ATT_NAME_FIELD][VALUE_FIELD]
                    new_optional_att[OPTIONAL_ATT_NAME_FIELD][VALUE_LABEL_FIELD_NEW] = att[OPTIONAL_ATT_NAME_FIELD][
                        VALUE_LABEL_FIELD_OLD]
                elif VALUE_FIELD in att[OPTIONAL_ATT_NAME_FIELD]:
                    new_optional_att[OPTIONAL_ATT_NAME_FIELD][VALUE_FIELD] = att[OPTIONAL_ATT_NAME_FIELD][VALUE_FIELD]
                # Optional attribute value
                if VALUE_LABEL_FIELD_OLD in att[OPTIONAL_ATT_VALUE_FIELD]:
                    new_optional_att[OPTIONAL_ATT_VALUE_FIELD][ID_FIELD] = att[OPTIONAL_ATT_VALUE_FIELD][VALUE_FIELD]
                    new_optional_att[OPTIONAL_ATT_VALUE_FIELD][VALUE_LABEL_FIELD_NEW] = att[OPTIONAL_ATT_VALUE_FIELD][
                        VALUE_LABEL_FIELD_OLD]
                elif VALUE_FIELD in att[OPTIONAL_ATT_VALUE_FIELD]:
                    new_optional_att[OPTIONAL_ATT_VALUE_FIELD][VALUE_FIELD] = att[OPTIONAL_ATT_VALUE_FIELD][VALUE_FIELD]
                instance[OPTIONAL_ATT_FIELD].append(new_optional_att)

    instance_ordered = OrderedDict(sorted(instance.items(), key=lambda t: get_sort_order(t)))

    return instance_ordered


def get_sort_order(item):
    field_name = item[0]
    if field_name in SORT_ORDER:
        return SORT_ORDER.index(field_name)
    else:
        return 1000


def update_instance_field_not_controlled(field_name, old_instance, new_instance):
    if field_name in old_instance:
        if (old_instance[field_name][VALUE_FIELD] is not None) and (
                    old_instance[field_name][VALUE_FIELD].strip() is not ""):
            new_instance[field_name][VALUE_FIELD] = old_instance[field_name][VALUE_FIELD]
        else:
            new_instance[field_name][VALUE_FIELD] = None
    else:
        new_instance[field_name] = {}
        new_instance[field_name][VALUE_FIELD] = None
    return new_instance


def update_instance_field_controlled(field_name, old_instance, new_instance):
    if (field_name in old_instance) and (VALUE_FIELD in old_instance[field_name]):
        if (old_instance[field_name][VALUE_FIELD] is not None) and (
                    old_instance[field_name][VALUE_FIELD].strip() is not ""):
            new_instance[field_name][ID_FIELD] = old_instance[field_name][VALUE_FIELD]
            new_instance[field_name][VALUE_LABEL_FIELD_NEW] = old_instance[field_name][VALUE_LABEL_FIELD_OLD]
            # else: do nothing
    return new_instance


if __name__ == "__main__": main()
