import subprocess
import argparse
import re
import json
from concurrent.futures import ThreadPoolExecutor
from rich.progress import Progress, TimeRemainingColumn, BarColumn
from rich.console import Console

parser = argparse.ArgumentParser()
parser.add_argument("--threads", "-t", help="Enter the number of threads you want to use", default=True)
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


with ThreadPoolExecutor(max_workers=args.threads) as executor:
    for url in urls:
        results.append((url, executor.submit(execute_script, url, args.script)))
    
    with Progress("[progress.description]{task.description}", BarColumn(),
                      "[progress.percentage]{task.percentage:>3.0f}%", TimeRemainingColumn(),
                      "[deep_sky_blue1]{task.completed} of {task.total}") as progress:
            my_task = progress.add_task("[green]Trying bypasses...", total=len(results))
            count_remaining = len(list(filter(lambda f: not f[1].done(), results)))
            while count_remaining > 0:
                count_remaining = len(list(filter(lambda f: not f[1].done(), results)))
                progress.update(my_task, completed=len(results) - count_remaining)
                time.sleep(1)

results = map(lambda r: (r[0], r[1].result()), results)
results = list(filter(lambda x: x[1], results))
print(json.dumps(results, indent=2))

if args.output:
    with open(args.output, "w") as handle:
        json.dump(results, handle, indent=2)
