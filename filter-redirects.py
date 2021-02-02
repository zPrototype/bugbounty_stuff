#!/usr/bin/python3
import requests
import argparse
from rich.progress import track

parser = argparse.ArgumentParser()
parser.add_argument("--file", "-f", required=True)
parser.add_argument("--dest", "-d", required=True)
parser.add_argument("--output", "-o", required=True)
args = parser.parse_args()

with open(args.file, "r") as handle:
    targets = handle.readlines()


def generate_domain_filter(dest):
    def specific_filter(target):
        try:
            res = requests.get(target, allow_redirects=True)
            if res.url.rstrip("/") in dest:
                return False
            return True
        except requests.exceptions.SSLError:
            pass
        except requests.exceptions.ConnectionError:
            pass
        except KeyboardInterrupt:
            print("Exiting...")
            exit()
        return False

    return specific_filter


my_filter = generate_domain_filter(args.dest)

targets = list(map(str.strip, targets))
data = list(filter(my_filter, track(targets, description="[yellow]Checking redirects...")))

with open(args.output, "w") as handle:
    handle.write("\n".join(data))

