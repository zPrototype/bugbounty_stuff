import pathlib
import re
import subprocess
import argparse
import sqlite3
import os
import shutil
import requests
import logging

from dataclasses import field, dataclass
from typing import Optional, List
from dataclasses_json import config, dataclass_json, Undefined
from rich.console import Console

TEMP_PATH = os.path.join(os.path.dirname(__file__), "_tmp")
CONSOLE = Console()

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-d", "--domain", help="Enter a domain you want to scan for subdomains eg. tesla.com")
group.add_argument("-f", "--file", help="Enter a file containing domains you want to scan for subdomains")
parser.add_argument("-o", "--output-dir", help="Specify the output directory",
                    type=pathlib.Path, default=os.getcwd())
parser.add_argument("-w", "--waybacks", action="store_true", help="Enable wayback scan. This might take a while.")
parser.add_argument("-sp", "--spyse_key", help="Enter your spyse api key if you have one")
parser.add_argument("-st", "--setrails_key", help="Enter your securitytrails api key if you have one")
args = parser.parse_args()

os.makedirs(TEMP_PATH, exist_ok=True)
os.makedirs(args.output_dir, exist_ok=True)
conn = sqlite3.connect(os.path.join(args.output_dir, "enumsubs.db"))

logFormatter = logging.Formatter("%(asctime)-15s [%(levelname)8s] [%(threadName)s] [%(name)-12s] - %(message)s")
LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler(os.path.join(args.output_dir, "subkiller.log"))
fileHandler.setFormatter(logFormatter)
LOG.addHandler(fileHandler)

LOG.info(f"Starting script run with args {args}")

def print_banner():
    print("""
███████╗██╗   ██╗██████╗ ██╗  ██╗██╗██╗     ██╗     ███████╗██████╗ 
██╔════╝██║   ██║██╔══██╗██║ ██╔╝██║██║     ██║     ██╔════╝██╔══██╗
███████╗██║   ██║██████╔╝█████╔╝ ██║██║     ██║     █████╗  ██████╔╝
╚════██║██║   ██║██╔══██╗██╔═██╗ ██║██║     ██║     ██╔══╝  ██╔══██╗
███████║╚██████╔╝██████╔╝██║  ██╗██║███████╗███████╗███████╗██║  ██║
╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝
                                                                    """)
    print("\033[1mDeveloped by iCaotix and 0xPrototype\033[0m\n")


def check_for_tools():
    required_tools = ["findomain", "subfinder", "sublist3r", "assetfinder", "gau", "httpx"]
    for tool in required_tools:
        check_tool_flag = shutil.which(tool)
        if check_tool_flag is None:
            CONSOLE.print(f"[bold red]{tool} is not installed! Exiting...")
            exit(1)


def bootstrab_db():
    conn.execute("CREATE TABLE IF NOT EXISTS domains (domain text unique)")
    conn.execute("CREATE TABLE IF NOT EXISTS rawsubdomains (subdomain text unique)")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS results (
        protocol text,
        domain text,
        port int,
        statuscodechain text,
        statuscode text,
        title text,
        redirectURL text,
        unique(domain,port)
    )""")
    conn.execute("CREATE TABLE IF NOT EXISTS waybackurls (ID INTEGER PRIMARY KEY AUTOINCREMENT, waybackurl text)")
    conn.commit()
    LOG.info("Database bootstrapped")


def insert_domains(domain_list):
    domain_list = list(map(lambda d: (d,), domain_list))
    conn.executemany("INSERT OR IGNORE INTO domains VALUES (?)", domain_list)
    conn.commit()
    LOG.info(f"starter domains inserted: {domain_list}")


def process_input():
    if args.file:
        with open(args.file, "r") as handle:
            domains = handle.readlines()
        domains = list(map(lambda d: d.strip(), domains))
    else:
        domains = [args.domain]
    return domains


def get_domains_to_scan():
    domains = conn.execute("SELECT * FROM domains")
    domains = map(lambda d: d[0], domains)
    return list(domains)


def start_scans(domain_list):
    LOG.info("Start scans")
    for target in domain_list:
        do_findomain_scan(target)
        do_sublist3r_scan(target)
        do_subfinder_scan(target)
        do_assetfinder_scan(target)
        do_crtsh_scan(target)


def do_crtsh_scan(target):
    LOG.info("Start crtsh scan")
    user_agent = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0"}
    url = f"https://crt.sh/?q={target}"
    response = requests.get(url, headers=user_agent)
    if not response.status_code == 200:
        LOG.warning("Failed to pull results from crt.sh")
        return
    output = response.text
    LOG.info(f"Pulled results from crt.sh with content length: {len(output)}")
    subdomain_regex = re.compile(f"[\w].*{target}")
    spaces_regex = re.compile("(.*[\ ].*)")
    result = re.findall(subdomain_regex, output.replace("TD>", "").replace("<BR>", "\n").replace("TD ", ""))
    result = [re.sub(spaces_regex, "", x) for x in set(result)]
    result = [elem for elem in result if elem.strip() != ""]
    result = list(map(lambda r: (r.strip(),), result))
    LOG.info(f"Completed crt.sh with {len(result)} results")
    conn.executemany("INSERT OR IGNORE INTO rawsubdomains VALUES (?)", result)
    conn.commit()
    LOG.info("Added results of crt.sh to database")


def do_findomain_scan(target):
    LOG.info("Start finddomain scan")
    env = {}
    if args.spyse_key:
        env["findomain_spyse_token"] = args.spyse_key
    if args.setrails_key:
        env["findomain_securitytrails_token"] = args.setrails_key

    findomain_cmd = f"findomain -t {target} -u {TEMP_PATH}/{target}.fd"
    if env:
        proc = subprocess.run(findomain_cmd, env=env, shell=True, stdout=subprocess.DEVNULL)
    else:
        proc = subprocess.run(findomain_cmd, shell=True, stdout=subprocess.DEVNULL)

    LOG.info(f"External process completed: {proc}")

    try:
        with open(f"{TEMP_PATH}/{target}.fd", "r") as handle:
            result = handle.readlines()
        LOG.info(f"Read result of finddomain with {len(result)} lines")
    except Exception:
        LOG.warning("Reading resultfile failed")
        return
    result = list(map(lambda r: (r.strip(),), result))
    conn.executemany("INSERT OR IGNORE INTO rawsubdomains VALUES (?)", result)
    conn.commit()
    LOG.info("Added results of finddomain to database")


def do_sublist3r_scan(target):
    LOG.info("Start sublist3r scan")
    sublist3r_cmd = f"sublist3r -d {target} -o {TEMP_PATH}/{target}.sl"
    proc = subprocess.run(sublist3r_cmd, shell=True, stdout=subprocess.DEVNULL)
    LOG.info(f"External process completed: {proc}")

    try:
        with open(f"{TEMP_PATH}/{target}.sl", "r") as handle:
            result = handle.readlines()
        LOG.info(f"Read result of sublist3r with {len(result)} lines")
    except Exception:
        LOG.warning("Reading resultfile failed")
        return
    result = list(map(lambda r: (r.strip(),), result))
    conn.executemany("INSERT OR IGNORE INTO rawsubdomains VALUES (?)", result)
    conn.commit()
    LOG.info("Added results of sublist3r to database")


def do_subfinder_scan(target):
    LOG.info("Start subfinder scan")
    subfinder_cmd = f"subfinder -d {target} -o {TEMP_PATH}/{target}.sf"
    proc = subprocess.run(subfinder_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                          stdin=subprocess.DEVNULL)
    LOG.info(f"External process completed: {proc}")

    try:
        with open(f"{TEMP_PATH}/{target}.sf", "r") as handle:
            result = handle.readlines()
        LOG.info(f"Read result of subfinder with {len(result)} lines")
    except Exception:
        LOG.warning("Reading resultfile failed")
        return
    result = list(map(lambda r: (r.strip(),), result))
    conn.executemany("INSERT OR IGNORE INTO rawsubdomains VALUES (?)", result)
    conn.commit()
    LOG.info("Added results of subfinder to database")


def do_assetfinder_scan(target):
    LOG.info("Start assetfinder scan")
    assetfinder_cmd = f"assetfinder --subs-only {target}"
    assetfinder_output = subprocess.check_output(assetfinder_cmd, shell=True, stdin=subprocess.DEVNULL)
    assetfinder_output = assetfinder_output.decode().splitlines()
    assetfinder_output = list(map(lambda r: (r.strip(),), assetfinder_output))
    LOG.info(f"Assetfinder returned: {len(assetfinder_output)} results")

    conn.executemany("INSERT OR IGNORE INTO rawsubdomains VALUES (?)", assetfinder_output)
    conn.commit()
    LOG.info("Added results of assetfinder to database")


def do_probing():
    subdomains = conn.execute("SELECT * FROM rawsubdomains")
    subdomains = map(lambda s: s[0], subdomains)
    with open(f"{TEMP_PATH}/unprobed.out", "w") as handle:
        handle.write('\n'.join(subdomains))

    httpx_cmd = f"httpx -l {TEMP_PATH}/unprobed.out -silent -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; " \
                "rv:55.0) Gecko/20100101 Firefox/55.0' -ports 80,8080,8081,8443,443,7001,3000 -status-code " \
                f"-no-color -follow-redirects -title -websocket -json -o {TEMP_PATH}/httpx_subs.txt"
    subprocess.run(httpx_cmd, shell=True, stdout=subprocess.DEVNULL)

    @dataclass_json(undefined=Undefined.EXCLUDE)
    @dataclass
    class HttpxOutput:
        scheme: Optional[str] = None
        port: Optional[int] = None
        url: Optional[str] = None
        title: Optional[str] = None
        statuscode: Optional[int] = field(metadata=config(field_name="status-code"), default=None)
        final_dest: Optional[str] = field(metadata=config(field_name="final-url"), default=None)
        statuscodes: Optional[List[int]] = field(metadata=config(field_name="chain-status-codes"), default=None)

        def get_db_tuple(self):
            domain = re.match(r"https?://([^:]*)(:\d*)?", self.url).groups()[0]
            return (
                self.scheme,
                domain,
                self.port,
                str(self.statuscodes),
                self.statuscode,
                self.title,
                self.final_dest
            )

    with open(f"{TEMP_PATH}/httpx_subs.txt") as handle:
        to_insert = [HttpxOutput.schema().loads(line).get_db_tuple() for line in handle.readlines()]

    conn.executemany("INSERT OR IGNORE INTO results VALUES (?, ?, ?, ?, ?, ?, ?)", to_insert)
    conn.commit()


def get_waybackurls(domain_list):
    for target in domain_list:
        gau_cmd = f"""bash -c "echo '{target}' | gau --blacklist ttf,woff,svg,png,jpg --o {TEMP_PATH}/{target}.gau" """
        subprocess.run(gau_cmd, shell=True, stdout=subprocess.DEVNULL)

        with open(f"{TEMP_PATH}/{target}.gau", "r") as handle:
            result = handle.readlines()
        result = list(map(lambda r: (r.strip(),), result))

        conn.executemany("INSERT OR IGNORE INTO waybackurls (waybackurl) VALUES (?)", result)
        conn.commit()


def get_screenshot_urls():
    urls_without_redirect = conn.execute(
        "SELECT redirectURL FROM results WHERE redirectURL IS NOT NULL AND statuscode = 200 "
        "UNION "
        "SELECT protocol || '://' || domain || ':' || port FROM results WHERE redirectURL IS NULL AND statuscode = 200")
    all_urls = list(map(lambda row: row[0], urls_without_redirect.fetchall()))
    return all_urls


def export_results():
    # master.txt
    results = conn.execute("SELECT protocol, domain, port FROM results WHERE statuscode != 429")
    export_lines = []
    for res in results:
        export_lines.append(f"{res[0]}://{res[1]}:{res[2]}")
    with open(os.path.join(args.output_dir, "master.txt"), "w") as handle:
        handle.write("\n".join(export_lines))

    # statuscodes.txt
    results = conn.execute(
        "SELECT protocol, domain, port, statuscode, title, redirectURL FROM results WHERE statuscode != 429")
    export_lines = []
    for res in results:
        export_lines.append(f"{res[0]}://{res[1]}:{res[2]} [{res[3]}] [{res[4]}] [{res[5] or ''}]")
    with open(os.path.join(args.output_dir, "statuscodes.txt"), "w") as handle:
        handle.write("\n".join(export_lines))

    # 403.txt
    results = conn.execute("SELECT protocol, domain, port FROM results WHERE statuscode == 403")
    export_lines = []
    for res in results:
        export_lines.append(f"{res[0]}://{res[1]}:{res[2]}")
    with open(os.path.join(args.output_dir, "403.txt"), "w") as handle:
        handle.write("\n".join(export_lines))

    # wayback.txt
    if args.waybacks:
        results = conn.execute("SELECT DISTINCT waybackurl FROM waybackurls")
        export_lines = map(lambda w: w[0], results)
        with open(os.path.join(args.output_dir, "waybacks.txt"), "w") as handle:
            handle.write("\n".join(export_lines))

    # screenshot_urls.txt
    export_lines = get_screenshot_urls()
    with open(os.path.join(args.output_dir, "screenshot_urls.txt"), "w") as handle:
        handle.write("\n".join(export_lines))


def cleanup():
    shutil.rmtree(TEMP_PATH)
    conn.execute("DELETE FROM domains")
    conn.commit()


def main():
    print_banner()
    with CONSOLE.status("") as status:
        check_for_tools()
        CONSOLE.print("[cyan]Tool check done!")
        bootstrab_db()
        CONSOLE.print("[cyan]Bootstrapped database!")
        requested_domains = process_input()
        insert_domains(requested_domains)
        domains_to_scan = get_domains_to_scan()
        status.update("[bold yellow]Scanning for subdomains...")
        start_scans(domains_to_scan)
        CONSOLE.print("[cyan]Scanning done!")
        status.update("[bold yellow]Probing subdomains...")
        do_probing()
        CONSOLE.print("[cyan]Probing done!")
        status.update("[bold yellow]Preparing urls for screenshooting")
        get_screenshot_urls()
        CONSOLE.print("[cyan]Screenshot urls ready!")
        if args.waybacks:
            status.update("[bold yellow]Searching for waybackurls...")
            get_waybackurls(domains_to_scan)
            CONSOLE.print("[cyan]Wayback scan done!")
        export_results()
        cleanup()
        CONSOLE.print("[cyan]Exported results")
        CONSOLE.print("[cyan]Cleaned temporary directory")
        print()
        CONSOLE.print("[bold green]Finished!")


if __name__ == '__main__':
    main()
