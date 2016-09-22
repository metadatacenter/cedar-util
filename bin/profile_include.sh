#!/bin/bash
#Shell aliases
alias ls='ls -laGp'
alias cls='clear'
alias hi='history'

#Colors for ls
export CLICOLOR=1
export LSCOLORS=gxBxhxDxfxhxhxhxhxcxcx

#CEDAR location aliases
alias gocedar='cd $CEDAR_HOME'
alias goparent='cd $CEDAR_HOME/cedar-parent'
alias goproject='cd $CEDAR_HOME/cedar-project'

alias goutil='cd $CEDAR_HOME/cedar-util'
alias goconf='cd $CEDAR_HOME/cedar-conf'
alias godocs='cd $CEDAR_HOME/cedar-docs'
alias goserverutils='cd $CEDAR_HOME/cedar-server-utils'

alias goprojectconfig='cd $CEDAR_HOME/cedar-project-config'
alias goadmintools='cd $CEDAR_HOME/cedar-admin-tools'

alias gofolder='cd $CEDAR_HOME/cedar-folder-server'
alias gorepo='cd $CEDAR_HOME/cedar-repo-server'
alias goresource='cd $CEDAR_HOME/cedar-resource-server'
alias goschema='cd $CEDAR_HOME/cedar-schema-server'
alias gotemplate='cd $CEDAR_HOME/cedar-template-server'
alias goterminology='cd $CEDAR_HOME/cedar-terminology-server/cedar-terminology-server-play'
alias gouser='cd $CEDAR_HOME/cedar-user-server'
alias govaluerecommender='cd $CEDAR_HOME/cedar-valuerecommender-server/cedar-valuerecommender-server-play'

alias gofolderplay='gofolder && cd cedar-folder-server-play'
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
alias killkk="kill `ps ax | grep \"[k]eycloak/standalone\" | awk '{print $1}'`";

#CEDAR server aliases
alias killbypid='kill `cat RUNNING_PID`'
alias starteditor='goeditor && gulp &'
alias killeditor='kill `pgrep gulp`'

alias startfolder='gofolder && mp2r &'
alias killfolder='gofolderplay && killbypid'
alias startrepo='gorepo && mp2r &'
alias killrepo='gorepoplay && killbypid'
alias startresource='goresource && mp2r &'
alias killresource='goresourceplay && killbypid'
alias startschema='goschema && mp2r &'
alias killschema='goschemaplay && killbypid'
alias starttemplate='gotemplate && mp2r &'
alias killtemplate='gotemplateplay && killbypid'
alias startterminology='goterminology && mp2r &'
alias killterminology='goterminologyplay && killbypid'
alias startuser='gouser && mp2r &'
alias killuser='gouserplay && killbypid'
alias startvaluerecommender='govaluerecommender && mp2r &'
alias killvaluerecommender='govaluerecommenderplay && killbypid'

alias killall='$CEDAR_HOME/cedar-util/bin/killall.sh'
alias startall='$CEDAR_HOME/cedar-util/bin/startall.sh'

alias startinfra='$CEDAR_HOME/cedar-util/bin/startinfra.sh'
