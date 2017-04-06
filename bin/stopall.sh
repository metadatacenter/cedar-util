#!/bin/bash
clear
echo --------------------------------------------------------------------------------
echo Stopping Dropwizard enabled CEDAR microservices
echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

shopt -s expand_aliases
source $CEDAR_HOME/cedar-util/bin/profile_include.sh

stopfolder
stoprepo
stopgroup
stopresource
stopschema
stoptemplate
stopterminology
stopuser
stopvaluerecommender
stopsubmission
stopworker