import requests
import argparse
from urllib3.exceptions import InsecureRequestWarning
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console

parser = argparse.ArgumentParser()
parser.add_argument("--file", "-f", help="Enter a file with URLs to check", required=True)
parser.add_argument("--output", "-o", help="Enter the name of a output file", required=True)
args = parser.parse_args()

CONSOLE = Console()
results = []

with open(args.file) as handle:
    urls = handle.readlines()
urls = list(map(lambda x: x.rstrip(), urls))


def make_request(url):
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    try:
        res = requests.get(url, verify=False, allow_redirects=False).status_code
    except:
        res = False
    return res

with ThreadPoolExecutor(max_workers=10) as executor:
    with CONSOLE.status("") as status:
        for i, url in enumerate(urls):
            status.update(f"[cyan]Working on statuscodes... ({i}/{len(urls)})")
            results.append((url, executor.submit(make_request, url)))

results = map(lambda r: (r[0], r[1].result()), results)
results = list(filter(lambda x: x[1], results))

for url, status_code in results:
    print(url, status_code)

with open(args.output, "w") as handle:
    handle.write("\n".join(f"{x[0]}, {x[1]}" for x in results))
