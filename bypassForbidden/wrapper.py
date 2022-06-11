import subprocess
import argparse
import re
import json
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.progress import track

parser = argparse.ArgumentParser()
parser.add_argument("--threads", "-t", help="Enter the number of threads you want to use", default=5, type=int)
parser.add_argument("--urls", "-u", help="Enter a file of URLs you want to test", required=True)
parser.add_argument("--script", "-s", help="Enter the path for the script", required=True)
parser.add_argument("--output", "-o", help="Enter the name for an output file")
args = parser.parse_args()

CONSOLE = Console()

with open(args.urls) as handle:
    urls = handle.readlines()
urls = list(map(lambda x: x.rstrip(), urls))

results = []
filter_400_codes = re.compile(r"4\d+")


def execute_script(forbidden_url, script):
    command = f"{script} -r -c {forbidden_url}"
    output = subprocess.check_output(f"{command}", shell=True, stderr=subprocess.PIPE)
    output = output.decode("UTF-8").splitlines()
    output = filter(lambda x: not x.startswith("[+]"), output)
    output = filter(lambda x: not re.findall(filter_400_codes, x), output)
    output = filter(lambda x: x, output)
    return list(output)


CONSOLE.print("[bold cyan]Trying bypasses...")
with ThreadPoolExecutor(max_workers=args.threads) as executor:
    for url in track(urls, total=len(urls), description="Working..."):
        results.append((url, executor.submit(execute_script, url, args.script)))

results = map(lambda r: (r[0], r[1].result()), results)
results = list(filter(lambda x: x[1], results))
print(json.dumps(results, indent=2))

if args.output:
    with open(args.output, "w") as handle:
        json.dump(results, handle, indent=2)
