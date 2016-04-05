#!/bin/bash
clear
echo ---------------------------------------------
echo Pulling all CEDAR repos
echo ---------------------------------------------
echo

RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
NORMAL=$(tput sgr0)
format="\n\nPulling Git repo status ${GREEN}%-20s${NORMAL} : (%-60s)\n"

function pullRepo {
	printf "$format" $1 $CEDAR_HOME$1
	git -C "$CEDAR_HOME$1" pull
	git -C "$CEDAR_HOME$1" status
	git -C "$CEDAR_HOME$1" status | grep 'Your branch is up-to-date with'
	if [ $? == 0 ]; then
		echo "${GREEN}Up-to-date with remote :)${NORMAL}"
	else
		echo "${RED}Something to do here!${NORMAL}"
	fi
}

pullRepo cedar-auth
pullRepo cedar-conf
pullRepo cedar-docs
pullRepo cedar-parent
pullRepo cedar-project
pullRepo cedar-repo-server
pullRepo cedar-resource-server
pullRepo cedar-schema-server
pullRepo cedar-server-utils
pullRepo cedar-template-editor
pullRepo cedar-template-server
pullRepo cedar-terminology-server
pullRepo cedar-user-server
pullRepo cedar-util
pullRepo cedar-valuerecommender-server
