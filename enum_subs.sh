#!/bin/bash

target=$1

findomain -t $target -u $target.fd
assetfinder --subs-only $target | tee $target.af
sublist3r -d $target -o ./$target.sl
subfinder -d $target -o $target.sf

sed -i 's/^\s*.*:\/\///g' $target.sl
cat $target.fd $target.af $target.sl $target.sf | sort -u | tee unprobed.out
cat unprobed.out | httpx -silent -H "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0" -ports 80,8080,8081,8443,443,7001,3000 -status-code -no-color -websocket -o httpx_subs.txt
cat httpx_subs.txt | grep -v "\[429\]" | tee $target.statuscodes.txt
cat $target.statuscodes.txt | grep "\[403\]" | awk '{print $1}' | sort -u | tee -a 403.txt
sed 's/:[^:]*//2g' $target.statuscodes.txt | sort -u | tee -a master.txt

cat $target.statuscodes.txt | tee -a statuscodes.txt

rm $target.fd $target.af $target.sl $target.sf $target.statuscodes.txt unprobed.out httpx_subs.txt

echo ""
echo "[+] Finished!"
