#!/bin/bash
clear

source $CEDAR_HOME/cedar-util/bin/include-colors-and-header.sh "Switching to new branch $1"
source $CEDAR_HOME/cedar-util/bin/include-repo-list.sh

format="\n\nSwitching Git repo ${GREEN}%-20s${NORMAL} : (%-60s)\n"

function createBranchInRepo {
	printf "$format" $1 $CEDAR_HOME$1
	git -C "$CEDAR_HOME$1" checkout -b $2
}

for i in "${CEDAR_REPOS[@]}"
do
   createBranchInRepo $i $1
done
