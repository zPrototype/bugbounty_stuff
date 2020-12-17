#!/bin/bash

dataset=$1
subdomains=$(cat $dataset)

for subdomain in $subdomains; do
	ShopifySubdomainTakeoverCheck.py $subdomain;
done
