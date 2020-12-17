#!/usr/bin/python3

import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--file", "-f", action="store", help="Enter path to a subdomain file", required=True)
args = parser.parse_args()

with open(args.file, "r") as handle:
    subdomains = handle.readlines()

for subdomain in subdomains:
    outfile = subdomain.strip() + "_res.txt"
    subprocess.call(f"assetfinder --subs-only {subdomain.strip()} | tee {outfile}", shell=True)
