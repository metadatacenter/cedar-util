#!/bin/bash
clear
echo ---------------------------------------------
echo Checking all CEDAR repos for changes
echo ---------------------------------------------
echo

RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
NORMAL=$(tput sgr0)
format="\n\nChecking Git repo status ${GREEN}%-20s${NORMAL} : (%-60s)\n"

function checkRepo {
	printf "$format" $1 $CEDAR_HOME$1
	git -C "$CEDAR_HOME$1" remote update
	git -C "$CEDAR_HOME$1" status
	git -C "$CEDAR_HOME$1" status | grep 'Your branch is up-to-date with'
	if [ $? == 0 ]; then
		echo "${GREEN}Up-to-date with remote :)${NORMAL}"
	else
		echo "${RED}Something to do here!${NORMAL}"
	fi
}

checkRepo cedar-admin-tools
checkRepo cedar-auth
checkRepo cedar-conf
checkRepo cedar-docs
checkRepo cedar-folder-server
checkRepo cedar-parent
checkRepo cedar-project
checkRepo cedar-repo-server
checkRepo cedar-resource-server
checkRepo cedar-schema-server
checkRepo cedar-server-utils
checkRepo cedar-template-editor
checkRepo cedar-template-server
checkRepo cedar-templates
checkRepo cedar-terminology-server
checkRepo cedar-user-server
checkRepo cedar-util
checkRepo cedar-valuerecommender-server
