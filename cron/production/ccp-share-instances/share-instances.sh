#!/bin/bash
#echo "Starting script to share instances of a given template with a given group:"
#echo "--------------------------------------------------------------------------"
export PATH="/home/cedar/anaconda3/bin:$PATH"
source activate py34
# Share instances of the 'CCP Digital Object' template
python /srv/cedar/cedar-util/scripts/python/group_permissions_to_instances.py https://repo.metadatacenter.org/templates/62c8b5f2-7dc9-4fff-9008-07c95a746411 https://repo.metadatacenter.org/groups/fd473979-33ab-4154-a316-de828dcf8cc0 read
# Share instances of 'COVID Project Admin' template with 'CEDAR Dev Team' group
python /srv/cedar/cedar-util/scripts/python/group_permissions_to_instances.py https://repo.metadatacenter.org/templates/eb3f3015-f776-4fc7-a074-7c113c4d0c0c https://repo.metadatacenter.net/groups/295c93d3-0c9b-430c-ba25-82f98ced501a read
python /srv/cedar/cedar-util/scripts/python/group_permissions_to_instances.py https://repo.metadatacenter.org/templates/3258a592-a0a0-4822-9eda-5cd757e28926 https://repo.metadatacenter.net/groups/295c93d3-0c9b-430c-ba25-82f98ced501a read
# Share instances of 'COVID Project Admin' template with 'ZonMW COVID Metadata' group
python /srv/cedar/cedar-util/scripts/python/group_permissions_to_instances.py https://repo.metadatacenter.org/templates/eb3f3015-f776-4fc7-a074-7c113c4d0c0c https://repo.metadatacenter.org/groups/89ae032c-48e1-4448-8c42-ca39c72f900b read
python /srv/cedar/cedar-util/scripts/python/group_permissions_to_instances.py https://repo.metadatacenter.org/templates/3258a592-a0a0-4822-9eda-5cd757e28926 https://repo.metadatacenter.org/groups/89ae032c-48e1-4448-8c42-ca39c72f900b read
python /srv/cedar/cedar-util/scripts/python/group_permissions_to_instances.py https://repo.metadatacenter.org/templates/1c645834-e593-479e-9e2a-026b858cb58a https://repo.metadatacenter.org/groups/89ae032c-48e1-4448-8c42-ca39c72f900b read
#echo "--------------------------------------------------------------------------"
#echo "Script execution finished."
