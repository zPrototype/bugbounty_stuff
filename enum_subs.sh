#!/bin/bash

target=$1

findomain -t $target -u $target.fd
assetfinder --subs-only $target | tee $target.af
sublist3r -d $target -o ./$target.sl

sed -i 's/^\s*.*:\/\///g' $target.sl
cat $target.fd $target.af $target.sl | sort -u | tee unprobed.out
cat unprobed.out | httpx -H "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0" -ports 80,8080,8081,8443,443,7001,3000 -status-code -no-color -websocket -o httpx_subs.txt
cat httpx_subs.txt | grep -v "\[429\]" | tee statuscodes.txt
cat statuscodes.txt | grep "\[403\]" | awk '{print $1}' | tee 403.txt
sed 's/:[^:]*//2g' statuscodes.txt | sort -u | tee master.txt

rm $target.fd $target.af $target.sl unprobed.out httpx_subs.txt

echo ""
echo "[+] Finished!"
