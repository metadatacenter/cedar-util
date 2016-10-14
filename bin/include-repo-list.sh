#!/bin/bash
CEDAR_REPOS=( "cedar-admin-tools" "cedar-conf" "cedar-docs" "cedar-folder-server" "cedar-model" "cedar-parent" "cedar-group-server" "cedar-project" "cedar-repo-server" "cedar-resource-server" "cedar-schema-server" "cedar-server-utils" "cedar-template-editor" "cedar-template-server" "cedar-terminology-server" "cedar-user-server" "cedar-util" "cedar-valuerecommender-server")

echo List of CEDAR repos:
for i in "${CEDAR_REPOS[@]}"
do
   echo "   - " $i
done