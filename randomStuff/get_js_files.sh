#!/bin/bash

urls=$1

cat $urls | waybackurls | tee waybacks/all_unprobed.txt
sed -i '/^$/d' waybacks/all_unprobed.txt
cat waybacks/all_unprobed | grep "\.js" | sort -u | tee waybacks/js_files.txt
python3 /root/recon-data/bugbounty_stuff/statusCodeGetter.py -f waybacks/js_files.txt -o waybacks/js_files_statuscodes.txt
