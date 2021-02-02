#!/bin/bash

target=$1

findomain -t $target -u ./$target.fd
assetfinder --subs-only $target | tee $target.af
sublist3r -d $target -o ./$target.sl

cat $target.fd $target.af $target.sl | sort -u | tee unprobed.out
cat unprobed.out | httprobe | tee master.txt
rm $target.fd $target.af $target.sl unprobed.out

echo ""
echo "[+] Finished!"
