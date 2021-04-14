#!/bin/bash

while getopts d:s:t: flag
do
	case "${flag}" in
		d) domain=${OPTARG};;
		s) spyse=${OPTARG};;
		t) setrails=${OPTARG};;
	esac
done

if [ -z "$domain" ]
then
	echo "Target parameter -d not specified!"
	exit
fi

fd_command="findomain -t ${domain} -u ${domain}.fd"

if [ ! -z "$spyse" ]
then
	fd_command="findomain_spyse_token=${spyse} ${fd_command}"
fi
if [ ! -z "$setrails" ]
then
	fd_command="findomain_securitytrails_token=${setrails} ${fd_command}"
fi

eval $fd_command
assetfinder --subs-only $domain | tee $domain.af
sublist3r -d $domain -o $domain.sl
subfinder -d $domain -o $domain.sf

sed -i 's/^\s*.*:\/\///g' $domain.sl
cat $domain.fd $domain.af $domain.sl $domain.sf | sort -u | tee unprobed.out
cat unprobed.out | httpx -silent -H "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0" -ports 80,8080,8081,8443,443,7001,3000 -status-code -no-color -websocket -o httpx_subs.txt
cat httpx_subs.txt | grep -v "\[429\]" | tee $domain.statuscodes.txt
cat $domain.statuscodes.txt | grep "\[403\]" | awk '{print $1}' | sort -u | tee -a 403.txt
sed 's/:[^:]*//2g' $domain.statuscodes.txt | sort -u | tee -a master.txt

cat $domain.statuscodes.txt | tee -a statuscodes.txt

rm $domain.fd $domain.af $domain.sl $domain.sf $domain.statuscodes.txt unprobed.out httpx_subs.txt

echo ""
echo "[+] Finished!"
