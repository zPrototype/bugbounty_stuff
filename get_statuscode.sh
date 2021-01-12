#!/bin/bash

subdomains=$1

while read subdomain; do
	status_code=$(curl -L -s -k -o /dev/null -w "%{http_code}" $subdomain)
	
	if [ $status_code -gt 499 ]; then
		continue
	fi
	
	echo -e $subdomain $status_code
done < $subdomains
