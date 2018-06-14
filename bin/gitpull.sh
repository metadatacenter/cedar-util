#!/bin/bash
source $CEDAR_HOME/$1/cedar-util/bin/include-colors-and-header.sh "Pulling all CEDAR repos"
source $CEDAR_HOME/$1/cedar-util/bin/include-repo-list.sh

format="\n\nPulling Git repo status ${GREEN}%-20s${NORMAL} : (%-60s)\n"

function pullRepo {
	printf "$format" $1 $CEDAR_HOME/$1
	git -C "$CEDAR_HOME/$1" pull
	git -C "$CEDAR_HOME/$1" status
	git -C "$CEDAR_HOME/$1" status | grep 'Your branch is up-to-date with'
	if [ $? == 0 ]; then
		echo "${GREEN}Up-to-date with remote :)${NORMAL}"
	else
		echo "${RED}Something to do here!${NORMAL}"
	fi
}

for i in "${CEDAR_REPOS[@]}"
do
   pullRepo $i
done