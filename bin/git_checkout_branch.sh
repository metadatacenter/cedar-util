#!/bin/bash
clear
echo ---------------------------------------------
echo Switching and pulling $@ branch
echo ---------------------------------------------
echo

RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
NORMAL=$(tput sgr0)
format="\n\nSwitching Git repo ${GREEN}%-20s${NORMAL} : (%-60s)\n"

function switchToRepo {
	printf "$format" $1 $CEDAR_HOME$1
	git -C "$CEDAR_HOME$1" checkout $2
	if [ $? == 0 ]; then
		echo "${GREEN}Up-to-date with remote :)${NORMAL}"
	else
		echo "${RED}Something went wrong here!${NORMAL}"
	fi
	git -C "$CEDAR_HOME$1" pull
}

switchToRepo cedar-auth $@
switchToRepo cedar-conf $@
switchToRepo cedar-docs $@
switchToRepo cedar-folder-server $@
switchToRepo cedar-parent $@
switchToRepo cedar-project $@
switchToRepo cedar-repo-server $@
switchToRepo cedar-resource-server $@
switchToRepo cedar-schema-server $@
switchToRepo cedar-server-utils $@
switchToRepo cedar-template-editor $@
switchToRepo cedar-template-server $@
switchToRepo cedar-templates $@
switchToRepo cedar-terminology-server $@
switchToRepo cedar-user-server $@
switchToRepo cedar-util $@
switchToRepo cedar-valuerecommender-server $@
switchToRepo cedar-admin-tools $@
