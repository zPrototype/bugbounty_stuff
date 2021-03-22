import requests
import argparse
import time
from urllib3.exceptions import InsecureRequestWarning
from concurrent.futures import ThreadPoolExecutor
from rich.progress import Progress, BarColumn, TimeRemainingColumn

parser = argparse.ArgumentParser()
parser.add_argument("--file", "-f", help="Enter a file with URLs to check", required=True)
parser.add_argument("--output", "-o", help="Enter the name of a output file", required=True)
parser.add_argument("--threads", "-t", help="Enter the number of threads. (Default is 10)", default=10)
args = parser.parse_args()

results = []

with open(args.file) as handle:
    urls = handle.readlines()
urls = list(map(lambda x: x.rstrip(), urls))


def make_request(url):
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    try:
        res = requests.get(url, verify=False, allow_redirects=False, timeout=10).status_code
    except:
        res = False
    return res


with ThreadPoolExecutor(max_workers=20) as executor:
    for i, url in enumerate(urls):
        results.append((url, executor.submit(make_request, url)))

    # Progress bar
    with Progress("[progress.description]{task.description}", BarColumn(),
                  "[progress.percentage]{task.percentage:>3.0f}%", TimeRemainingColumn(),
                  "[deep_sky_blue1]{task.completed} of {task.total}") as progress:
        my_task = progress.add_task("[green]Working on it...", total=len(results))
        count_remaining = len(list(filter(lambda f: not f[1].done(), results)))
        while count_remaining > 0:
            count_remaining = len(list(filter(lambda f: not f[1].done(), results)))
            progress.update(my_task, completed=len(results) - count_remaining)
            time.sleep(1)

results = map(lambda r: (r[0], r[1].result()), results)
results = list(filter(lambda x: x[1], results))

for url, status_code in results:
    print(url, status_code)

with open(args.output, "w") as handle:
    handle.write("\n".join(f"{x[0]} {x[1]}" for x in results))
