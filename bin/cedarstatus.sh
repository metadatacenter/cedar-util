#!/bin/bash
clear
echo ---------------------------------------------
echo Checking all CEDAR servers
echo ---------------------------------------------
echo

format="| %-27s| %-20s| %-15s| %10s | %-20s|\n"
header="| %-27s| %-9s| %-15s| %10s | %-20s|\n"
RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
NORMAL=$(tput sgr0)

function checkStatus {
        if pgrep -f "$2" > /dev/null 2>&1
        then
                status="${GREEN}Running${NORMAL}"
        else
                status="${RED}Stopped${NORMAL}"
        fi
        printf "$format" $1 $status 'pgrep' ' ' $2
}

function checkHealth {
        if curl -I -s http://localhost:$2/healthcheck | grep "200 OK" > /dev/null 2>&1
        then
                status="${GREEN}Running${NORMAL}"
        else
                status="${RED}Stopped${NORMAL}"
        fi
        printf "$format" $1 $status 'healthCheck' $2 ' '
}

function checkHttpResponse {
        ok=1
        if curl -I -s http://localhost:$2 | grep "$3" > /dev/null 2>&1
        then
                status="${GREEN}Running${NORMAL}"
        else
                status="${RED}Stopped${NORMAL}"
                ok=0
        fi
        printf "$format" $1 $status 'httpResponse' $2 $3
        if ((ok == 0));
        then
                echo ---------- $1 ERROR
                echo 'http://localhost:'$2
                curl -I http://localhost:$2
                echo --------------------------------------
        fi
}


echo ----------------------------------------------------------------------------------------
printf "$header" 'Server' 'Status' 'CheckedFor' 'Port' 'Value'
echo ----------------------------------------------------------------------------------------
printf "$header" '--- Microservices ---------'
checkStatus Folder port=9008
checkHealth Group 9109
checkStatus User port=9005
checkStatus Repo port=9002
checkStatus Resource port=9007
checkHealth Schema 9103
checkStatus Template port=9001
checkStatus Terminology port=9004
checkStatus ValueRecommender port=9006
printf "$header" '--- Infrastructure --------'
checkStatus MongoDB mongod
checkHttpResponse Elasticsearch 9200 '200\sOK'
checkHttpResponse Kibana 5601 'kbn-name:\skibana'
checkHttpResponse NGINX 80 'Server:\snginx'
checkHttpResponse Keycloak 8080 'Server:\sWildFly'
checkHttpResponse Neo4j 7474 'Server:\sJetty'
printf "$header" '--- Development Front End -'
checkStatus Gulp gulp
