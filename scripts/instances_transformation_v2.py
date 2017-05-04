#!/usr/bin/python

# 2016-May-4
# instances_transformation.py: Utility to transform ImmPort and ISA instances generated in Jan/Feb 2016
# to instances that follow the latest version of CEDAR Template Model.

import json
import sys
import os.path
import uuid
import time
import datetime

from pprint import pprint

def decrease_arrays_size(tree, max_size_general, max_size_process):
    restart = True
    while restart:
        restart = False
        if type(tree) is not unicode:
            for key in tree.iterkeys():
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


#############################################

if (len(sys.argv) != 3) or (len(sys.argv) == 3 and sys.argv[1] != '-immport' and sys.argv[1] != '-isa'):
    print('Please use the syntax: instances_transformation.py [-immport|-isa] instances_file.json')
else:
    print('Transforming instances...')
    data_source = sys.argv[1][1:]
    with open(sys.argv[2]) as input_file:
        input_file_name = sys.argv[2]
        data = json.load(input_file)
    
    #data = data['investigation']
    output = data
    
    if data_source == 'immport':
        # Constants
        MAX_STUDIES = 10
        # Arrays size limits for better loading performance at the Template Editor
        MAX_SIZE_GENERAL = 5
        MAX_SIZE_PROCESS = 1
        del output['templateId']
    elif data_source == 'isa':
        MAX_STUDIES = 10
        MAX_SIZE_GENERAL = 10
        MAX_SIZE_PROCESS = 10


    # Decrease arrays size
    decrease_arrays_size(output, MAX_SIZE_GENERAL, MAX_SIZE_PROCESS)

    investigationId = output['identifier']['_value'].replace("/", "") 
    studyId = output['study'][0]['identifier']['_value'].replace("/", "") 

    del output['@id']
    output['_templateId'] = 'https://repo.metadatacenter.net/templates/4681316c-b51c-4665-b5c3-1e3173cdd102'
    output['_ui'] = {}
    if data_source == 'immport':
        output['_ui']['templateTitle'] = 'Immport Investigation instance ' + investigationId + ' ' + studyId
        output['_ui']['templateDescription'] = 'Immport Investigation instance'
    elif data_source == 'isa':
        output['_ui']['templateTitle'] = 'ISA Investigation instance ' + investigationId + ' ' + studyId
        output['_ui']['templateDescription'] = 'ISA Investigation instance'
   
    folderName = 'transformed_data/' + data_source

    if not os.path.exists(folderName):
        os.makedirs(folderName)

    output_file_path = folderName + '/' +  os.path.splitext(os.path.split(input_file_name)[1])[0] + '_' + investigationId + '_' + studyId + '.json'
    with open(output_file_path, 'w') as output_file:
        json.dump(output, output_file, indent=2)
    
    print(output_file_path)
