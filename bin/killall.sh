#!/bin/bash
clear
echo ---------------------------------------------
echo Stopping Play enabled CEDAR microservices
echo ---------------------------------------------
echo

shopt -s expand_aliases
source $CEDAR_HOME/cedar-util/bin/profile_include.sh

killfolder
killrepo
killresource
killschema
killtemplate
killterminology
killuser
killvaluerecommender