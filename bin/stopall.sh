#!/bin/bash
clear
echo --------------------------------------------------------------------------------
echo Stopping Dropwizard enabled CEDAR microservices
echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

shopt -s expand_aliases
source $CEDAR_HOME/cedar-util/bin/profile_include.sh

stopworkspace
stoprepo
stopgroup
stopmessaging
stopresource
stopschema
stoptemplate
stopterminology
stopuser
stopvaluerecommender
stopsubmission
stopworker