#!/bin/bash

mkdir -p out

while read url; do
	filename=$(echo $url | sha256sum | awk '{print $1}')
	filename="out/$filename"
	echo "$filename $url" | tee -a index
	curl -sk -v "$url" &> $filename
done
