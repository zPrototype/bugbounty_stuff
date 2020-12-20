#!/bin/bash

urls=$1
hakrawler_out=$2

while IFS= read -r line; do
	hakrawler -url $line -plain | tee -a $hakrawler_out
done < $urls

while read hak_url; do
	python3 /opt/XSStrike/xsstrike.py -u $hak_url 2>/dev/null
done < $hakrawler_out
