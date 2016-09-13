#!/bin/bash
source $CEDAR_HOME/cedar-util/bin/include-colors-and-header.sh "Switching and pulling $@ branch"
source $CEDAR_HOME/cedar-util/bin/include-repo-list.sh

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

for i in "${CEDAR_REPOS[@]}"
do
   switchToRepo $i $@
done