#!/bin/bash
#echo "Starting script to share instances of a given template with a given group:"
#echo "--------------------------------------------------------------------------"

# Share instances of the 'CCP Digital Object' template
python3 /srv/cedar/cedar-util/scripts/python/group_permissions_to_instances.py https://repo.metadatacenter.org/templates/62c8b5f2-7dc9-4fff-9008-07c95a746411 https://repo.metadatacenter.org/groups/fd473979-33ab-4154-a316-de828dcf8cc0 read
# Share instances of 'COVID Project Admin' template with 'CEDAR Dev Team' group
python3 /srv/cedar/cedar-util/scripts/python/group_permissions_to_instances.py https://repo.metadatacenter.org/templates/eb3f3015-f776-4fc7-a074-7c113c4d0c0c https://repo.metadatacenter.net/groups/295c93d3-0c9b-430c-ba25-82f98ced501a read
python3 /srv/cedar/cedar-util/scripts/python/group_permissions_to_instances.py https://repo.metadatacenter.org/templates/3258a592-a0a0-4822-9eda-5cd757e28926 https://repo.metadatacenter.net/groups/295c93d3-0c9b-430c-ba25-82f98ced501a read
# Share instances of 'COVID Project Admin' template with 'ZonMW COVID Metadata' group
python3 /srv/cedar/cedar-util/scripts/python/group_permissions_to_instances.py https://repo.metadatacenter.org/templates/eb3f3015-f776-4fc7-a074-7c113c4d0c0c https://repo.metadatacenter.org/groups/89ae032c-48e1-4448-8c42-ca39c72f900b read
python3 /srv/cedar/cedar-util/scripts/python/group_permissions_to_instances.py https://repo.metadatacenter.org/templates/337cb6f3-eef6-4b2f-9ffb-3f6d6cc9b9ac https://repo.metadatacenter.org/groups/89ae032c-48e1-4448-8c42-ca39c72f900b read
# Share instances of 'COVID Project Content' template (different versions/copies of it) with 'ZonMW COVID Metadata' group
python3 /srv/cedar/cedar-util/scripts/python/group_permissions_to_instances.py https://repo.metadatacenter.org/templates/3258a592-a0a0-4822-9eda-5cd757e28926 https://repo.metadatacenter.org/groups/89ae032c-48e1-4448-8c42-ca39c72f900b read
python3 /srv/cedar/cedar-util/scripts/python/group_permissions_to_instances.py https://repo.metadatacenter.org/templates/1c645834-e593-479e-9e2a-026b858cb58a https://repo.metadatacenter.org/groups/89ae032c-48e1-4448-8c42-ca39c72f900b read
python3 /srv/cedar/cedar-util/scripts/python/group_permissions_to_instances.py https://repo.metadatacenter.org/templates/f697ab8d-7b71-4d48-9caf-8c256eb8ee13 https://repo.metadatacenter.org/groups/89ae032c-48e1-4448-8c42-ca39c72f900b read
python3 /srv/cedar/cedar-util/scripts/python/group_permissions_to_instances.py https://repo.metadatacenter.org/templates/8bcd40b3-ddb3-4b1f-af77-b3fe034c3db3 https://repo.metadatacenter.org/groups/89ae032c-48e1-4448-8c42-ca39c72f900b read
python3 /srv/cedar/cedar-util/scripts/python/group_permissions_to_instances.py https://repo.metadatacenter.org/templates/908e33e2-9485-4a93-ab22-1688dc5819dc https://repo.metadatacenter.org/groups/89ae032c-48e1-4448-8c42-ca39c72f900b read
python3 /srv/cedar/cedar-util/scripts/python/group_permissions_to_instances.py https://repo.metadatacenter.org/templates/28d58a30-1a42-4715-a742-d2f46690563e https://repo.metadatacenter.org/groups/89ae032c-48e1-4448-8c42-ca39c72f900b read
python3 /srv/cedar/cedar-util/scripts/python/group_permissions_to_instances.py https://repo.metadatacenter.org/templates/22925909-9fb2-4ac8-a986-6db5ae7049e7 https://repo.metadatacenter.org/groups/89ae032c-48e1-4448-8c42-ca39c72f900b read
python3 /srv/cedar/cedar-util/scripts/python/group_permissions_to_instances.py https://repo.metadatacenter.org/templates/de169781-7f75-4aef-a0cb-ac435fe3a4c7 https://repo.metadatacenter.org/groups/89ae032c-48e1-4448-8c42-ca39c72f900b read
#echo "--------------------------------------------------------------------------"
#echo "Script execution finished."
