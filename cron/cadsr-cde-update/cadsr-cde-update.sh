echo "Starting script to update CEDAR caDSR CDEs and Categories at" `date +%Y-%m-%dT%H:%M:%S`
echo "-----------------------------------------------------------------------------------"
cd $CEDAR_HOME/cedar-cadsr-tools
/usr/share/apache-maven/bin/mvn clean install -Dmaven.test.skip=true
/usr/share/apache-maven/bin/mvn exec:java@cedar-cadsr-updater -Dexec.args="--update-categories --update-cdes --server local --folder $CEDAR_CDE_FOLDER_ID --apikey $CEDAR_CADSR_ADMIN_USER_API_KEY --ftp-host $CEDAR_NCI_CADSR_FTP_HOST --ftp-user $CEDAR_NCI_CADSR_FTP_USER --ftp-password $CEDAR_NCI_CADSR_FTP_PASSWORD --ftp-categories-folder $CEDAR_NCI_CADSR_FTP_CLASSIFICATIONS_DIRECTORY --ftp-cdes-folder $CEDAR_NCI_CADSR_FTP_CDES_DIRECTORY --ontology-folder $CEDAR_HOME/cedar-shared-data/cadsr/ontologies"
echo "-----------------------------------------------------------------------------------"
echo "Script execution finished."