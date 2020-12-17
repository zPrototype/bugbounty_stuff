import socket
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("--file", "-f", action="store", help="Enter hosts file", required=True)
args = parser.parse_args()

host_dict = {}
host_list = []

with open(args.file, "r") as handle:
    hosts = handle.readlines()

for host in hosts:
    host = host.strip()
    ip = socket.gethostbyname(host)
    host_dict[host] = ip
    host_string = f"{host},{ip}"
    host_list.append(host_string)

with open("hosts.json", "w") as json_outfile:
    json.dump(host_dict, json_outfile, separators=(',', ':'))

with open("hosts.txt", "a") as txt_outfile:
    [txt_outfile.write(f"{element}\n") for element in host_list]