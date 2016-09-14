#!/bin/bash
clear
echo ---------------------------------------------
echo Switching and pulling develop branch
echo ---------------------------------------------
echo

$CEDAR_HOME$1/cedar-util/bin/git-checkout-branch.sh develop
