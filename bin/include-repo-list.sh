#!/bin/bash
CEDAR_REPOS=( "cedar-admin-tools" "cedar-conf" "cedar-docs" "cedar-folder-server" "cedar-group-server" "cedar-keycloak-event-listener" "cedar-model" "cedar-parent" "cedar-parent-dw" "cedar-project" "cedar-repo-server" "cedar-resource-server" "cedar-schema-server" "cedar-server-core-library" "cedar-template-editor" "cedar-template-server" "cedar-terminology-server" "cedar-user-server" "cedar-util" "cedar-valuerecommender-server")

echo List of CEDAR repos:
for i in "${CEDAR_REPOS[@]}"
do
   echo "   - " $i
done