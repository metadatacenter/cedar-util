# CEDAR-Elasticsearch operations module

SERVER = 'http://localhost:9200'

import requests
import json


# Get instance by instance id
def get_instace_by_id(instance_id):
    url = SERVER + "/cedar-search/content/_search"
    headers = {
        'content-type': "application/json"
    }
    payload = {
        "query": {
            "term": {
                "cid": instance_id
            }
        }
    }
    recommendation_response = requests.post(url, json=payload, headers=headers, verify=False)
    response = json.loads(recommendation_response.text)
    if len(response['hits']['hits']) > 0:
        return response['hits']['hits'][0]
    else:
        return None

# Remove instance from the index by instance id
def remove_instance_by_id(instance_id):
    instance = get_instace_by_id(instance_id)
    if instance is not None:
        # Elasticsearch id
        es_id = instance['_id']
        routing = instance['_routing']

        url = SERVER + "/cedar-search/content/" + es_id
        querystring = {"routing": routing}
        headers = {
            'content-type': "application/json"
        }
        delete_response = requests.delete(url, headers=headers, params=querystring, verify=False)
        # print("DELETE instance response: " + str(delete_response.status_code))
        if delete_response.status_code == 200:
            print("Instance removed from index: " + instance_id)
        else:
            print("ERROR! Couldn't remove instance from index: " + instance_id)
    else:
        print("Instance not found: " + instance_id)
