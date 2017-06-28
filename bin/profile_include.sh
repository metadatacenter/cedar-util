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
alias goparent='cd $CEDAR_HOME/cedar-parent'
alias goproject='cd $CEDAR_HOME/cedar-project'

alias goutil='cd $CEDAR_HOME/cedar-util'
alias goconf='cd $CEDAR_HOME/cedar-conf'
alias godocs='cd $CEDAR_HOME/cedar-docs'
alias goservercore='cd $CEDAR_HOME/cedar-server-core-library'
alias gomodel='cd $CEDAR_HOME/cedar-model-validation-library'

alias goadmintool='cd $CEDAR_HOME/cedar-admin-tool'

alias gofolder='cd $CEDAR_HOME/cedar-folder-server'
alias gogroup='cd $CEDAR_HOME/cedar-group-server'
alias gorepo='cd $CEDAR_HOME/cedar-repo-server'
alias goresource='cd $CEDAR_HOME/cedar-resource-server'
alias goschema='cd $CEDAR_HOME/cedar-schema-server'
alias gotemplate='cd $CEDAR_HOME/cedar-template-server'
alias goterminology='cd $CEDAR_HOME/cedar-terminology-server'
alias gouser='cd $CEDAR_HOME/cedar-user-server'
alias govaluerecommender='cd $CEDAR_HOME/cedar-valuerecommender-server'
alias gosubmission='cd $CEDAR_HOME/cedar-submission-server'
alias goworker='cd $CEDAR_HOME/cedar-worker-server'

alias goeventlistener='cd $CEDAR_HOME/cedar-keycloak-event-listener'

alias goeditor='cd $CEDAR_HOME/cedar-template-editor'

alias gokk='cd $KEYCLOAK_HOME/bin'

#CEDAR util aliases
alias cedargstatus='$CEDAR_HOME/cedar-util/bin/gitstatus.sh'
alias cedargbranches='$CEDAR_HOME/cedar-util/bin/gitbranches.sh'
alias cedargpull='$CEDAR_HOME/cedar-util/bin/gitpull.sh'
alias cedarenv='set | grep -a CEDAR_'
alias cedarat='$CEDAR_HOME/cedar-admin-tool/dist/cedar-admin-tool.sh'
alias cedargcheckout='$CEDAR_HOME/cedar-util/bin/git-checkout-branch.sh'


#Maven aliases
alias mi='mvn install'
alias mcl='mvn clean'
alias mci='mvn clean install'
alias mit='mvn install -DskipTests=true'
alias mcit='mvn clean install -DskipTests=true'

#Maven and shell aliases
alias m2clean='rm -rf ~/.m2/repository/*'
alias m2cleancedar='rm -rf ~/.m2/repository/org/metadatacenter/*'

#3rd party server aliases
alias startnginx='$CEDAR_HOME/cedar-util/bin/startnginx.sh'
alias stopnginx='$CEDAR_HOME/cedar-util/bin/stopnginx.sh'

alias startkk='$CEDAR_HOME/cedar-util/bin/startkeycloak.sh'
alias killkk='$CEDAR_HOME/cedar-util/bin/killkeycloak.sh'

alias startmongo='$CEDAR_HOME/cedar-util/bin/startmongo.sh'
alias stopmongo='$CEDAR_HOME/cedar-util/bin/stopmongo.sh'

alias startkibana='$CEDAR_HOME/cedar-util/bin/startkibana.sh'
alias stopkibana='$CEDAR_HOME/cedar-util/bin/stopkibana.sh'

alias startelastic='$CEDAR_HOME/cedar-util/bin/startelastic.sh'
alias stopelastic='$CEDAR_HOME/cedar-util/bin/stopelastic.sh'

alias startneo='$CEDAR_HOME/cedar-util/bin/startneo.sh'
alias stopneo='$CEDAR_HOME/cedar-util/bin/stopneo.sh'

alias startredis='$CEDAR_HOME/cedar-util/bin/startredis.sh'
alias stopredis='$CEDAR_HOME/cedar-util/bin/stopredis.sh'

#CEDAR server aliases
alias starteditor='goeditor && gulp &'
alias stopeditor='kill `pgrep gulp`'

alias startfolder='$CEDAR_UTIL_BIN/start-dw-server.sh folder &'
alias stopfolder='$CEDAR_UTIL_BIN/stop-dw-server.sh folder 9208'
alias startgroup='$CEDAR_UTIL_BIN/start-dw-server.sh group &'
alias stopgroup='$CEDAR_UTIL_BIN/stop-dw-server.sh group 9209'
alias startrepo='$CEDAR_UTIL_BIN/start-dw-server.sh repo &'
alias stoprepo='$CEDAR_UTIL_BIN/stop-dw-server.sh repo 9202'
alias startresource='$CEDAR_UTIL_BIN/start-dw-server.sh resource &'
alias stopresource='$CEDAR_UTIL_BIN/stop-dw-server.sh resource 9207'
alias startschema='$CEDAR_UTIL_BIN/start-dw-server.sh schema &'
alias stopschema='$CEDAR_UTIL_BIN/stop-dw-server.sh schema 9203'
alias starttemplate='$CEDAR_UTIL_BIN/start-dw-server.sh template &'
alias stoptemplate='$CEDAR_UTIL_BIN/stop-dw-server.sh template 9201'
alias startterminology='$CEDAR_UTIL_BIN/start-dw-server.sh terminology &'
alias stopterminology='$CEDAR_UTIL_BIN/stop-dw-server.sh terminology 9204'
alias startuser='$CEDAR_UTIL_BIN/start-dw-server.sh user &'
alias stopuser='$CEDAR_UTIL_BIN/stop-dw-server.sh user 9205'
alias startvaluerecommender='$CEDAR_UTIL_BIN/start-dw-server.sh valuerecommender &'
alias stopvaluerecommender='$CEDAR_UTIL_BIN/stop-dw-server.sh valuerecommender 9206'
alias startsubmission='$CEDAR_UTIL_BIN/start-dw-server.sh submission &'
alias stopsubmission='$CEDAR_UTIL_BIN/stop-dw-server.sh submission 9210'
alias startworker='$CEDAR_UTIL_BIN/start-dw-server.sh worker &'
alias stopworker='$CEDAR_UTIL_BIN/stop-dw-server.sh worker 9211'

alias stopall='$CEDAR_HOME/cedar-util/bin/stopall.sh'
alias startall='$CEDAR_HOME/cedar-util/bin/startall.sh'

alias startinfra='$CEDAR_HOME/cedar-util/bin/startinfra.sh'
alias stopinfra='$CEDAR_HOME/cedar-util/bin/stopinfra.sh'

alias ij="'/Applications/IntelliJ IDEA.app/Contents/MacOS/idea'"
