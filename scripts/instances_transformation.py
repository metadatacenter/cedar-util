#!/usr/bin/python

# 2015-Nov-8
# instances_transformation.py: Utility to transform ImmPort and ISA instances generated in October 2015
# to instances that follow the latest version of CEDAR Repository Model.

import json
import sys
import os.path
import uuid
import time
import datetime

from pprint import pprint

def update_name(tree, old_k, new_k):
    restart = True
    while restart:
        restart = False
        for key in tree.keys():
            # print key
            if key == old_k:
                tree[new_k] = tree[old_k]
                del tree[old_k]
                restart = True
            elif type(tree[key]) is dict:
                update_name(tree[key], old_k, new_k)
            elif type(tree[key]) is list:
                for item in tree[key]:
                    update_name(item, old_k, new_k)

# Updates 'value' to '_value' when appropriate
def update_value(tree):
    restart = True
    while restart:
        restart = False
        for key in tree.keys():
            if key == 'value':
                if tree[key] == 'https://schema.org/value':
                    tree['_value'] = tree['value']
                    del tree['value']
                    restart = True
                elif (not type(tree[key]) is dict) and (not type(tree[key]) is list):
                    if (type(tree[key]) is str):
                        if tree[key][:4] != 'http':
                            tree['_value'] = tree['value']
                            del tree['value']
                            restart = True
                    else:
                        tree['_value'] = tree['value']
                        del tree['value']
                        restart = True
                elif type(tree[key]) is dict:
                    update_value(tree[key])
                elif type(tree[key]) is list:
                    for item in tree[key]:
                        update_value(item)
            elif type(tree[key]) is dict:
                update_value(tree[key])
            elif type(tree[key]) is list:
                for item in tree[key]:
                    update_value(item)

# Shows 'N/A' instead of empty values
def fill_empty_values(tree, new_value):
    for key in tree.keys():
        if key == '_value' and tree[key] == '':
            tree[key] = new_value
        elif type(tree[key]) is dict:
            fill_empty_values(tree[key], new_value)
        elif type(tree[key]) is list:
            for item in tree[key]:
                fill_empty_values(item, new_value)

def decrease_arrays_size(tree, max_size_general, max_size_process):
    restart = True
    while restart:
        restart = False
        for key in tree.keys():
            if type(tree[key]) is list:
                if (key == 'process'):
                    if len(tree[key]) > max_size_process:
                        new_list = tree[key][0:max_size_process]
                        tree[key] = new_list
                        restart = True
                    else:
                        for item in tree[key]:
                            decrease_arrays_size(item, max_size_general, max_size_process)
                else:
                    if len(tree[key]) > max_size_general:
                        new_list = tree[key][0:max_size_general]
                        tree[key] = new_list
                        restart = True
                    else:
                        for item in tree[key]:
                            decrease_arrays_size(item, max_size_general, max_size_process)
            elif type(tree[key]) is dict:
                decrease_arrays_size(tree[key], max_size_general, max_size_process)

def remove_empty_fields(tree):
    restart = True
    while restart:
        restart = False
        for key in tree.keys():
            if type(tree[key]) is dict:
                if not tree[key]:
                    del tree[key]
                    restart = True
                    break
                else:
                    remove_empty_fields(tree[key])
            elif type(tree[key]) is list:
                if not tree[key]:
                    del tree[key]
                    restart = True
                    break
                for item in tree[key]:
                    remove_empty_fields(item)
            

#############################################

if (len(sys.argv) != 3) or (len(sys.argv) == 3 and sys.argv[1] != '-immport' and sys.argv[1] != '-isa'):
    print('Please use the syntax: instances_transformation.py [-immport|-isa] instances_file.json')
else:
    print('Transforming instances...')
    data_source = sys.argv[1][1:]
    with open(sys.argv[2]) as input_file:
        input_file_name = sys.argv[2]
        data = json.load(input_file)
    
    data = data['investigation']
    output = data
    
    update_name(output, 'hasStudy', 'study')
    update_name(output, 'hasPublication', 'publication')
    update_name(output, 'hasContact', 'contact')
    update_name(output, 'hasAffiliation', 'organization')
    update_name(output, 'hasStudyProtocol', 'studyProtocol')
    update_name(output, 'executeStudyProtocol', 'studyProtocol')
    update_name(output, 'hasProtocolParameter', 'protocolParameter')
    update_name(output, 'hasParameterValue', 'parameterValue')
    update_name(output, 'hasStudyAssay', 'studyAssay')
    update_name(output, 'hasProcess', 'process')
    update_name(output, 'hasStudyGroupPopulation', 'studyGroupPopulation')
    update_name(output, 'hasStudyFactor', 'studyFactor')
    update_name(output, 'hasInput', 'input')
    update_name(output, 'hasOutput', 'output')
    update_name(output, 'hasCharacteristic', 'characteristic')
    update_name(output, 'hasCharacteristicValue', 'characteristicValue')
    update_name(output, 'hasStudySubject', 'studySubject')
    update_name(output, 'hasReagent', 'reagent')
    update_name(output, 'hasCollectionStudyTime', 'studyTime')
    update_name(output, 'hasSample', 'sample')
    update_name(output, 'hasResult', 'result')
    update_name(output, 'hasResultValue', 'resultValue')
    update_name(output, 'hasDataFile', 'dataFile')
    update_name(output, 'hasFactorValue', 'factorValue')
    update_name(output, 'uri', 'uRI')
    update_name(output, 'doi', 'dOI')
    # Update value to _value
    update_value(output)

    # Fill out empty values to 'N/A'
    #fill_empty_values(output, 'N/A')

    if data_source == 'immport':
        # Constants
        MAX_STUDIES = 10
        # Arrays size limits for better loading performance at the Template Editor
        MAX_SIZE_GENERAL = 5
        MAX_SIZE_PROCESS = 1
    elif data_source == 'isa':
        MAX_STUDIES = 10
        MAX_SIZE_GENERAL = 8
        MAX_SIZE_PROCESS = 8

    # Transformation rules
    for s in output['study']:
        for p in s['process']:
            # Correction: process-studyAssay should be an array but it is not
            studyAssayArray = []
            studyAssayArray.append(p['studyAssay'])
            p['studyAssay'] = studyAssayArray
            
            # Correction: process-studyProtocol should be an array but it is not
            studyProtocolArray = []
            studyProtocolArray.append(p['studyProtocol'])
            p['studyProtocol'] = studyProtocolArray
            
            input_temp = p ['input']
            p['input'] = {}
            p['input']['sample'] = []
            p['input']['reagent'] = []
            p['input']['studySubject'] = []
            p['input']['result'] = []
            p['input']['dataFile'] = []
            for inp in input_temp:
                if inp['@type'] == 'https://repo.metadatacenter.org/model/Sample':
                    sample = {}
                    sample['@type'] = inp['@type']
                    sample['name'] = inp['name']
                    sample['type'] = inp['type']
                    sample['description'] = inp['description']
                    sample['source'] = inp['source']
                    sample['studyTime'] = inp['studyTime']
                    sample['factorValue'] = inp['factorValue']
                    p['input']['sample'].append(sample)
                elif inp['@type'] == 'https://repo.metadatacenter.org/model/Reagent':
                    reagent = {}
                    reagent['@type'] = inp['@type']
                    reagent['name'] = inp['name']
                    reagent['type'] = inp['type']
                    reagent['characteristic'] = inp['characteristic']
                    p['input']['reagent'].append(reagent)
                elif inp['@type'] == 'https://repo.metadatacenter.org/model/StudySubject':
                    studySubject = {}
                    studySubject['@type'] = inp['@type']
                    studySubject['name'] = inp['name']
                    studySubject['type'] = inp['type']
                    studySubject['characteristic'] = inp['characteristic']
                    p['input']['studySubject'].append(studySubject)
                elif inp['@type'] == 'https://repo.metadatacenter.org/model/Result':
                    result = {}
                    result['@type'] = inp['@type']
                    result['name'] = inp['name']
                    result['description'] = inp['type']
                    result['resultValue'] = inp['resultValue']
                    p['input']['result'].append(result)
                elif inp['@type'] == 'https://repo.metadatacenter.org/model/DataFile':
                    dataFile = {}
                    dataFile['@type'] = inp['@type']
                    dataFile['name'] = inp['name']
                    dataFile['description'] = inp['description']
                    p['input']['dataFile'].append(dataFile)
            
            output_temp = p ['output']
            p['output'] = {}
            p['output']['sample'] = []
            p['output']['result'] = []
            p['output']['dataFile'] = []
            for out in output_temp:
                if out['@type'] == 'https://repo.metadatacenter.org/model/Sample':
                    sample = {}
                    sample['@type'] = out['@type']
                    sample['name'] = out['name']
                    sample['type'] = out['type']
                    sample['description'] = out['description']
                    sample['source'] = out['source']
                    sample['studyTime'] = out['studyTime']
                    sample['factorValue'] = out['factorValue']
                    sample['characteristic'] = out['characteristic']
                    sample['studyTime'] = out['studyTime']
                    sample['factorValue'] = out['factorValue']
                    p['output']['sample'].append(sample)
                elif out['@type'] == 'https://repo.metadatacenter.org/model/Result':
                    result = {}
                    result['@type'] = out['@type']
                    result['name'] = out['name']
                    result['description'] = out['type']
                    result['resultValue'] = out['resultValue']
                    p['output']['result'].append(result)
                elif inp['@type'] == 'https://repo.metadatacenter.org/model/DataFile':
                    dataFile = {}
                    dataFile['@type'] = out['@type']
                    dataFile['name'] = out['name']
                    dataFile['description'] = inp['description']
                    p['output']['dataFile'].append(dataFile)

    ### ImmPort Specific Transformation Rules ###
    if (data_source == 'immport'):
        # Remove redundant data
        for s in output['study']:
            for p in s['process']:
                del p['studyAssay']
                del p['studyProtocol']
                del p['input']['studySubject']
                for sam in p['input']['sample']:
                    for fv in sam['factorValue']:
                        del fv['studyFactor']

    ### ISA Specific Transformation Rules ###
    elif (data_source == 'isa'):          
        # Remove redundant data
        for s in output['study']:
             for p in s['process']:
                 del p['studyAssay']
                 del p['studyProtocol']

    # Decrease arrays size
    decrease_arrays_size(output, MAX_SIZE_GENERAL, MAX_SIZE_PROCESS)

    # Remove empty fields
    remove_empty_fields(output)
    remove_empty_fields(output)

    # with open(os.path.splitext(sys.argv[1])[0] + '_transformed.json', 'w') as output_file:
    # json.dump(output, output_file, indent=2)

    # Save studies in independent files for better performance when loading them with the template editor
    all_studies = output['study']
    limit = min(MAX_STUDIES, len(all_studies))
    print('Transformed instances have been saved to: ')
    for i in range(0,limit):
        
        del output['study']
        output['study'] = []
        output['study'].append(all_studies[i])

        investigationId = output['identifier']['_value']
        studyId = output['study'][0]['identifier']['_value']

        folderName = 'transformed_data/' + data_source

        output['template_id'] = 'https://repo.metadatacenter.org/406d3a6d-c264-417a-bf30-bd6273762bd8'
        output['info'] = {}
        output['info']['template_description'] = 'Investigation instance' 
        output['info']['creation_date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output['info']['template_title'] = data_source + '-' + investigationId + '-' + studyId
        output['@id'] = 'https://repo.metadatacenter.org/' + str(uuid.uuid4())
        
        if not os.path.exists(folderName):
            os.makedirs(folderName)

        output_file_path = folderName + '/' +  os.path.splitext(os.path.split(input_file_name)[1])[0] + '-' + investigationId + '-' + studyId + '.json'
        with open(output_file_path, 'w') as output_file:
            json.dump(output, output_file, indent=2)
    
        print(output_file_path)
