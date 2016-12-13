#!/bin/bash
#Shell aliases
alias ls='ls -laGp'
alias cls='clear'
alias hi='history'

#Colors for ls
export CLICOLOR=1
export LSCOLORS=gxBxhxDxfxhxhxhxhxcxcx

#Common CEDAR locations
export CEDAR_UTIL_BIN=$CEDAR_HOME/cedar-util/bin

#CEDAR location aliases
alias gocedar='cd $CEDAR_HOME'
alias goparent='cd $CEDAR_HOME/cedar-parent'
alias goproject='cd $CEDAR_HOME/cedar-project'

alias goutil='cd $CEDAR_HOME/cedar-util'
alias goconf='cd $CEDAR_HOME/cedar-conf'
alias godocs='cd $CEDAR_HOME/cedar-docs'
alias goservercore='cd $CEDAR_HOME/cedar-server-core-library'

alias goprojectconfig='cd $CEDAR_HOME/cedar-project-config'
alias goadmintools='cd $CEDAR_HOME/cedar-admin-tools'

alias gofolder='cd $CEDAR_HOME/cedar-folder-server'
alias gogroup='cd $CEDAR_HOME/cedar-group-server'
alias gorepo='cd $CEDAR_HOME/cedar-repo-server'
alias goresource='cd $CEDAR_HOME/cedar-resource-server'
alias goschema='cd $CEDAR_HOME/cedar-schema-server'
alias gotemplate='cd $CEDAR_HOME/cedar-template-server'
alias goterminology='cd $CEDAR_HOME/cedar-terminology-server/cedar-terminology-server-play'
alias gouser='cd $CEDAR_HOME/cedar-user-server'
alias govaluerecommender='cd $CEDAR_HOME/cedar-valuerecommender-server'

alias gofolderplay='gofolder && cd cedar-folder-server-play'
alias gogroupplay='gogroup && cd cedar-group-server-play'
alias gorepoplay='gorepo && cd cedar-repo-server-play'
alias goresourceplay='goresource && cd cedar-resource-server-play'
alias goschemaplay='goschema && cd cedar-schema-server-play'
alias gotemplateplay='gotemplate && cd cedar-template-server-play'
alias goterminologyplay='goterminology'
alias gouserplay='gouser && cd cedar-user-server-play'
alias govaluerecommenderplay='govaluerecommender'

alias goeditor='cd $CEDAR_HOME/cedar-template-editor'

alias gokk='cd $KEYCLOAK_HOME/bin'

#CEDAR util aliases
alias cedargstatus='$CEDAR_HOME/cedar-util/bin/gitstatus.sh'
alias cedargpull='$CEDAR_HOME/cedar-util/bin/gitpull.sh'
alias cedarss='$CEDAR_HOME/cedar-util/bin/cedarstatus.sh'
alias cedarenv='set | grep -a CEDAR_'
alias cedarat='$CEDAR_HOME/cedar-admin-tools/dist/cedar-admin-tools.sh'

#Maven aliases
alias mi='mvn install'
alias mcl='mvn clean'
alias mci='mvn clean install'
alias mit='mvn install -DskipTests=true'
alias mcit='mvn clean install -DskipTests=true'
alias mp2r='mvn play2:run'

#Maven and shell aliases
alias m2clean='rm -rf ~/.m2/repository/*'
alias m2cleancedar='rm -rf ~/.m2/repository/org/metadatacenter/*'

#3rd party server aliases
alias startnginx='sudo nginx'
alias stopnginx='sudo nginx -s stop'
alias restartnginx='sudo nginx -s stop && sudo nginx'
alias startkk='$KEYCLOAK_HOME/bin/standalone.sh &'
alias killkk='$CEDAR_HOME/cedar-util/bin/killkeycloak.sh'
alias stopmongo='$CEDAR_HOME/cedar-util/bin/killmongo.sh'
alias stopkibana='$CEDAR_HOME/cedar-util/bin/killkibana.sh'
alias stopelastic='$CEDAR_HOME/cedar-util/bin/killelastic.sh'

#CEDAR server aliases
alias killbypid='kill `cat RUNNING_PID`'
alias starteditor='goeditor && gulp &'
alias killeditor='kill `pgrep gulp`'

alias startfolder='$CEDAR_UTIL_BIN/start-dw-server.sh folder 9208 &'
alias stopfolder='$CEDAR_UTIL_BIN/stop-dw-server.sh 9208'
alias startgroup='$CEDAR_UTIL_BIN/start-dw-server.sh group 9209 &'
alias stopgroup='$CEDAR_UTIL_BIN/stop-dw-server.sh 9209'
alias startrepo='$CEDAR_UTIL_BIN/start-dw-server.sh repo 9202 &'
alias stoprepo='$CEDAR_UTIL_BIN/stop-dw-server.sh 9202'
alias startresource='$CEDAR_UTIL_BIN/start-dw-server.sh resource 9207 &'
alias stopresource='$CEDAR_UTIL_BIN/stop-dw-server.sh 9207'
alias startschema='$CEDAR_UTIL_BIN/start-dw-server.sh schema 9203 &'
alias stopschema='$CEDAR_UTIL_BIN/stop-dw-server.sh 9203'
alias starttemplate='$CEDAR_UTIL_BIN/start-dw-server.sh template 9201 &'
alias stoptemplate='$CEDAR_UTIL_BIN/stop-dw-server.sh 9201'
alias startterminology='goterminology && mp2r &'
alias killterminology='goterminologyplay && killbypid'
alias startuser='$CEDAR_UTIL_BIN/start-dw-server.sh user 9205 &'
alias stopuser='$CEDAR_UTIL_BIN/stop-dw-server.sh 9205'
alias startvaluerecommender='$CEDAR_UTIL_BIN/start-dw-server.sh valuerecommender 9206 &'
alias stopvaluerecommender='$CEDAR_UTIL_BIN/stop-dw-server.sh 9206'

alias stopall='$CEDAR_HOME/cedar-util/bin/stopall.sh'
alias startall='$CEDAR_HOME/cedar-util/bin/startall.sh'

alias startinfra='$CEDAR_HOME/cedar-util/bin/startinfra.sh'
alias stopinfra='$CEDAR_HOME/cedar-util/bin/stopinfra.sh'
