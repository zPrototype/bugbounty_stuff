#!/bin/bash

organization=$1
dataset=$2

subdomains=$(cat $dataset)

for subdomain in $subdomains; do
	ip=$(getent hosts $subdomain | awk '{print $1}')
	org=$(whois $ip | grep "OrgName:")
	if [[ $org == *$organization* ]]; then
		echo "$subdomain with ip $ip may be vulnerable to subdomain takeover!"
	fi
done
