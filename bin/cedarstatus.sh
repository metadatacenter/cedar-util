#!/bin/bash
clear
echo ---------------------------------------------
echo Checking all CEDAR servers
echo ---------------------------------------------
echo

format="| %-27s| %-19s| %-12s|%5s| %-18s|\n"
header="| %-27s| %-8s| %-12s|%5s| %-18s|\n"
RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
NORMAL=$(tput sgr0)

function checkOpenedPort {
        if nc -z localhost "$2" > /dev/null 2>&1
        then
                status="${GREEN}Running${NORMAL}"
        else
                status="${RED}Stopped${NORMAL}"
        fi
        printf "$format" $1 $status 'openedPort' $2
}

function checkHealth {
        ok=1
        lookFor='HTTP/1.1\s200\sOK'
        if curl -I -s http://localhost:$2/healthcheck | grep $lookFor > /dev/null 2>&1
        then
                status="${GREEN}Running${NORMAL}"
        else
                status="${RED}Stopped${NORMAL}"
                ok=0
        fi
        printf "$format" $1 $status 'healthCheck' $2 $lookFor
        if ((ok == 0));
        then
                reportError $1 $2
        fi
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
                reportError $1 $2
        fi
}

function checkRedisPing {
        ok=1
        if (printf "PING\r\nQUIT\r\n";) | nc localhost $2 | grep "+PONG" > /dev/null 2>&1
        then
                status="${GREEN}Running${NORMAL}"
        else
                status="${RED}Stopped${NORMAL}"
                ok=0
        fi
        printf "$format" $1 $status 'redisPing' $2 $3
        if ((ok == 0));
        then
                reportError $1 $2
        fi
}

function printLine {
        printf '|'
        printf $1'%.0s' {1..78}
        printf '|'
        printf '\n'
}

function reportError {
return
        printLine '.'
        echo '  -- ERROR IN '$1
        echo '  -- http://localhost:'$2
        curl -I http://localhost:$2
        printLine '^'
}

printLine '='

printf "$header" 'Server' 'Status' 'CheckedFor' 'Port' 'Value'

printLine '\x2D'

printf "$header" '--- Microservices ---------'
checkHealth Folder 9108
checkHealth Group 9109
checkHealth User 9105
checkHealth Repo 9102
checkHealth Resource 9107
checkHealth Schema 9103
checkHealth Template 9101
checkHealth Terminology 9104
checkHealth ValueRecommender 9106
checkHealth Submission 9110
checkHealth Worker 9111
printf "$header" '--- Infrastructure --------'
checkOpenedPort MongoDB 27017
checkHttpResponse Elasticsearch 9200 'HTTP/1.1\s200\sOK'
checkHttpResponse Kibana 5601 'kbn-name:\skibana'
checkHttpResponse NGINX 80 'Server:\snginx'
checkHttpResponse Keycloak 8080 'Server:\sWildFly'
checkHttpResponse Neo4j 7474 'Server:\sJetty'
checkRedisPing Redis-persistent 6379
#checkRedisPing Redis-non-persistent 6380
printf "$header" '--- Development Front End -'
checkHttpResponse Gulp 4200 'HTTP/1.1\s200\sOK'

printLine '='
