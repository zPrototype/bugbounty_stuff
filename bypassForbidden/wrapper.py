import subprocess
import argparse
import re
import json
from concurrent.futures import ThreadPoolExecutor

parser = argparse.ArgumentParser()
parser.add_argument("--urls", "-u", help="Enter a file of URLs you want to test", required=True)
parser.add_argument("--script", "-s", help="Enter the path for the script", required=True)
parser.add_argument("--output", "-o", help="Enter the name for an output file")
args = parser.parse_args()

with open(args.urls) as handle:
    urls = handle.readlines()
urls = list(map(lambda x: x.rstrip(), urls))

results = []
filter_400_codes = re.compile(r"4\d+")


def execute_script(url, script):
    command = f"{script} -r -c {url}"
    output = subprocess.check_output(f"{command}", shell=True, stderr=subprocess.PIPE)
    output = output.decode("UTF-8").splitlines()
    output = filter(lambda x: not x.startswith("[+]"), output)
    output = filter(lambda x: not re.findall(filter_400_codes, x), output)
    output = filter(lambda x: x, output)
    return list(output)


with ThreadPoolExecutor(max_workers=4) as executor:
    for url in urls:
        results.append((url, executor.submit(execute_script, url, args.script)))

results = map(lambda r: (r[0], r[1].result()), results)
results = list(filter(lambda x: x[1], results))
print(json.dumps(results, indent=2))

if args.output:
    with open(args.output, "w") as handle:
        json.dump(results, handle, indent=2)
