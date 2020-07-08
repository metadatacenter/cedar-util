#!/bin/bash 

###################################################################
# Script Name	: CEDAR Patch                                                                                             
# Description	: Executes the Python scripts that patches CEDAR 
#                 artifacts in a MongoDB database                                                                                                                                                  
###################################################################

HOSTNAME=$(hostname)
HOSTNAME_CEDAR_STAGING="cedr-dev-app-01.stanford.edu"
HOSTNAME_CEDAR_PRODUCTION="cedr-dev-app-02.stanford.edu"
CURRENTDATE=$(date +"%Y-%m-%d")
CURRENTDATETIME=$(date +"%Y-%m-%d-%T")
OUTPUTDB="cedar-patched-${CURRENTDATE}"

banner()
{
  echo "+------------------------------------------+"
  printf "|           CEDAR Patch Script             |\n"
  printf "| %-40s |\n" "`date`"
  echo "|                                          |"
  printf "|`tput bold` %-40s `tput sgr0`|\n" "$@"
  echo "+------------------------------------------+"
}

banner "Starting..."
sleep 1

cd "${CEDAR_HOME}/cedar-util/scripts/python" || exit

# Create log folder if it does not exist
if [ ! -d "${CEDAR_HOME}/log/cedar-patch" ]; then
  mkdir -p "${CEDAR_HOME}/log/cedar-patch";
fi

LOG_FILE_PATH="${CEDAR_HOME}/log/cedar-patch/${CURRENTDATETIME}_patch.log"

echo "This script will patch all CEDAR artifacts in your MongoDB 'cedar' database and will store them into a new"
echo "database '$OUTPUTDB'. The original 'cedar' database will remain untouched. After running this script,"
echo "you can use the CEDAR tool 'mongo-rename.py' to replace the original database with the patched one."
echo
read -p "Press Enter to continue "
echo
sleep 1

while true; do
    read -p "What do you want to do when a patched resource is invalid? Enter 'y' to save the patched resource or 'n' to save the original one. " yn
    case $yn in
        [Yy]* ) FORCE=true; break;;
        [Nn]* ) FORCE=false; break;;
        * ) echo "Please answer yes or no.";;
    esac
done

echo

if [ "$HOSTNAME" == "$HOSTNAME_CEDAR_STAGING" ] || [ "$HOSTNAME" == "$HOSTNAME_CEDAR_PRODUCTION" ];
	then
		if [ "$HOSTNAME" == "$HOSTNAME_CEDAR_STAGING" ];
			then
				echo "Your are running this script on CEDAR's Staging server"
			else
				echo "Your are running this script on CEDAR's Production server"
		fi
		echo "Activating Python environment..."
    source activate py34
    echo "Python environment activated."
    echo "Starting CEDAR patch Python script..."
    if [ "$FORCE" == true ];
      then
		    python -u -m cedar.patch2.cedar_patch2 -r all -i cedar -o "$OUTPUTDB" -f | tee "$LOG_FILE_PATH"
		  else
		    python -u -m cedar.patch2.cedar_patch2 -r all -i cedar -o "$OUTPUTDB" | tee "$LOG_FILE_PATH"
		fi
	else
	  if [ "$FORCE" == true ];
	    then
		    python3 -u -m cedar.patch2.cedar_patch2 -r all -i cedar -o "$OUTPUTDB" -f | tee "$LOG_FILE_PATH"
		  else
		    python3 -u -m cedar.patch2.cedar_patch2 -r all -i cedar -o "$OUTPUTDB" | tee "$LOG_FILE_PATH"
		fi
fi

echo
echo "Standard output saved to $LOG_FILE_PATH"


banner "Finished."


