import time
from types import SimpleNamespace
import requests
import argparse
import json
import urllib.parse
from rich.console import Console

parser = argparse.ArgumentParser()
parser.add_argument("--dorks", "-d", help="Enter the file with github dorks", required=True)
parser.add_argument("--access_key", "-a", help="Enter list of access keys to avoid rate limiting", required=True)
parser.add_argument("--target", "-t", help="Enter the name of the target organization", required=True)
parser.add_argument("--output", "-o", help="Enter output filename")
args = parser.parse_args()

# Globals
HEADER = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0",
    "Authorization": f"token {args.access_key}"
}
MAX_KEY_USAGE = 29
CONSOLE = Console()


def filter_data(curr_result):
    if not curr_result[0]:
        return False
    if curr_result[0].total_count == 0:
        return False
    return True


def main():
    with open(args.dorks) as handle:
        dorks = handle.readlines()
    dorks = list(map(lambda x: urllib.parse.quote_plus(x.rstrip()), dorks))

    CONSOLE.print("[bold yellow]This may take a while!")
    results = []
    with CONSOLE.status("") as status:
        for i, dork in enumerate(dorks):
            status.update(f"[cyan]Working on dorks... ({i}/{len(dorks)})")
            if i % MAX_KEY_USAGE == 0 and i != 0:
                CONSOLE.print("[bold red]Sleeping to avoid rate limit...")
                time.sleep(61)
            url = f"https://api.github.com/search/code?q=org%3A{args.target}%20{dork}"
            res = requests.get(url, headers=HEADER, timeout=10)
            res_json = json.loads(res.text, object_hook=lambda o: SimpleNamespace(**o))
            results.append((res_json, dork))
            CONSOLE.print(f"Finished dork: {urllib.parse.unquote_plus(dork)}")

    results = list(filter(filter_data, results))
    for result in results:
        print(f"Found {result[0].total_count} results for: {result[1]}")
        if args.output:
            with open(args.output, "a") as handle:
                handle.write(f"Found {result[0].total_count} results for: {urllib.parse.unquote_plus(result[1])}\n")
    CONSOLE.print("[bold green]Finished!")


if __name__ == '__main__':
    main()
