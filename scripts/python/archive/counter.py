#!/usr/bin/python

# counter.py: Utility to count the number of instances of different types in a CEDAR ISA-ImmPort model data dump
# Syntax: counter.py input.json output.csv

import json
import sys
import csv

from pprint import pprint

if (len(sys.argv) != 3):
    print('Please use the syntax: counter.py input.json output.csv')
else:
    with open(sys.argv[1]) as data_file:
        data = json.load(data_file)

    investigation_details = []
    investigation_count = 1
    study_count = 0
    for study in data['investigation']['hasStudy']:
        study_count += 1
        # publication_count = 0
        # contact_count = 0
        # study_protocol_count = 0
        # study_assay_count = 0
        # process_count = 0
        # study_group_population_count = 0
        # study_factor_count = 0
        print('')
        print('- Study: ' + str(study_count))

        publication_count = len(study['hasPublication'])
        print('Publication: ' + str(publication_count))

        contact_count = len(study['hasContact'])
        print('Contact: ' + str(contact_count))

        organization_count = 0
        for contact in study['hasContact']:
            organization_count += len(contact['hasAffiliation'])
        print('Organization: ' + str(organization_count))

        study_protocol_count = len(study['hasStudyProtocol'])
        print('Study Protocol: ' + str(study_protocol_count))

        protocol_parameter_count = 0
        for study_protocol in study['hasStudyProtocol']:
            protocol_parameter_count += len(study_protocol['hasProtocolParameter'])
        print('Protocol Parameter: ' + str(protocol_parameter_count))

        study_assay_count = len(study['hasStudyAssay'])
        print('Study Assay: ' + str(study_assay_count))

        process_count = len(study['hasProcess'])
        print('Process: ' + str(process_count))

        total_inputs = 0
        total_outputs = 0
        result_count = 0
        result_value_count = 0
        data_file_count = 0
        sample_count = 0
        reagent_count = 0
        study_time_count = 0
        factor_value_count = 0
        for process in study['hasProcess']:
            # Outputs
            for output in process['hasOutput']:
                total_outputs += 1
                if output['@type'] == 'https://repo.metadatacenter.org/model/Result':
                    result_count += 1
                    if len(output['hasResultValue']['value']['value']) > 0:
                        result_value_count += 1
                if output['@type'] == 'https://repo.metadatacenter.org/model/DataFile':
                    data_file_count += 1
                if output['@type'] == 'https://repo.metadatacenter.org/model/Sample':
                    sample_count += 1
                    if output['hasCollectionStudyTime']['durationValue'] > 0:
                        study_time_count += 1
                    factor_value_count = len(output['hasFactorValue'])
            # Inputs
            for input in process['hasInput']:
                total_inputs += 1
                if output['@type'] == 'https://repo.metadatacenter.org/model/Reagent':
                    reagent_count += 1

        print('Result: ' + str(result_count))
        print('Result Value: ' + str(result_value_count))
        print('Data File: ' + str(data_file_count))
        print('Sample: ' + str(sample_count))
        print('Reagent: ' + str(reagent_count))
        print('.Total inputs: ' + str(total_inputs))
        print('.Total outputs: ' + str(total_outputs))

        parameter_value_count = 0
        for process in study['hasProcess']:
            parameter_value_count += len(process['hasParameterValue'])
        print('Parameter Value: ' + str(parameter_value_count))

        study_group_population_count = len(study['hasStudyGroupPopulation'])
        print('Study Group Population: ' + str(study_group_population_count))

        study_subject_count = 0
        characteristic_count = 0
        characteristic_value_count = 0
        for study_group_factor_population in study['hasStudyGroupPopulation']:
            study_subject_count += len(study_group_factor_population['hasStudySubject'])
            for study_subject in study_group_factor_population['hasStudySubject']:
                characteristic_count += len(study_subject['hasCharacteristic'])
                for characteristic in study_subject['hasCharacteristic']:
                    if len(characteristic['hasCharacteristicValue']['value']['value']) > 0:
                        characteristic_value_count += 1
        print('Study Subject: ' + str(study_subject_count))
        print('Characteristic: ' + str(characteristic_count))
        print('Characteristic Value: ' + str(characteristic_value_count))

        study_factor_count = len(study['hasStudyFactor'])
        print('Study Factor: ' + str(study_factor_count))

        study_details = [1, publication_count, contact_count, organization_count, study_protocol_count,
                         protocol_parameter_count, study_assay_count, process_count, total_inputs, total_outputs,
                         result_count, result_value_count, data_file_count, sample_count, reagent_count, study_time_count,
                         factor_value_count, parameter_value_count, study_group_population_count, study_subject_count,
                         characteristic_count, characteristic_value_count, study_factor_count]
        investigation_details.append(study_details)

    with open(sys.argv[2], 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(["Study",
                             "Publication",
                             "Contact",
                             "Organization",
                             "Study Protocol",
                             "Protocol Parameter",
                             "Study Assay",
                             "Process",
                             "Inputs",
                             "Outputs",
                             "Result",
                             "Result Value",
                             "Data File",
                             "Sample",
                             "Reagent",
                             "Study Time",
                             "Factor Value",
                             "Parameter Value",
                             "Study Group Population",
                             "Study Subject",
                             "Characteristic",
                             "Characteristic Value",
                             "Study Factor"])
        for s in investigation_details:
            spamwriter.writerow(s)
