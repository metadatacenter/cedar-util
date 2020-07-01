#!/bin/bash
source activate py34
CURRENTDATE=`date +"%Y-%m-%d"`
python -m cedar.patch2.cedar_patch2 -r all -i cedar -o cedar-patched-${CURRENTDATE} | tee /srv/cedar/log/cedar-patch/${CURRENTDATE}_patch.log
