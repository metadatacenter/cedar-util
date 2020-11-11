#!/bin/bash
#echo "Starting script to share instances of a given template with a given group:"
#echo "--------------------------------------------------------------------------"
export PATH="/home/cedar/anaconda3/bin:$PATH"
source activate py34
python /srv/cedar/cedar-util/scripts/group_permissions_to_instances.py
#echo "--------------------------------------------------------------------------"
#echo "Script execution finished."