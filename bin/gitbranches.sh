#!/bin/bash

source $CEDAR_HOME$1/cedar-util/bin/include-repo-list.sh

function show_branch {
	branch=$(git rev-parse --abbrev-ref HEAD)
	cd $CEDAR_HOME$1
	printf "  (%s) %s\n" $branch $1
}

echo $'\n Current Git branches: '
for i in "${CEDAR_REPOS[@]}"
do
	show_branch $i
done
