import pathlib
import re
import subprocess
import argparse
import sqlite3
import os
import shutil
import requests
import logging
import urllib3

from urllib3 import exceptions
from dataclasses import field, dataclass
from typing import Optional, List
from dataclasses_json import config, dataclass_json, Undefined
from rich.console import Console

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
TEMP_PATH = os.path.join(os.path.dirname(__file__), "_tmp")
CONSOLE = Console()


def get_arguments():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--domain", help="Enter a domain you want to scan for subdomains eg. tesla.com")
    group.add_argument("-f", "--file", help="Enter a file containing domains you want to scan for subdomains")
    parser.add_argument("-o", "--output-dir", help="Specify the output directory", type=pathlib.Path, default=os.getcwd())
    parser.add_argument("-w", "--waybacks", action="store_true", help="Enable wayback scan. This might take a while.")
    parser.add_argument("-sp", "--spyse_key", help="Enter your spyse api key if you have one")
    parser.add_argument("-st", "--setrails_key", help="Enter your securitytrails api key if you have one")
    return parser.parse_args()


def get_logger(logfile_dir: str):
    log_formatter = logging.Formatter("%(asctime)-15s [%(levelname)8s] [%(threadName)s] [%(name)-12s] - %(message)s")
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(os.path.join(logfile_dir, "subkiller.log"))
    file_handler.setFormatter(log_formatter)
    log.addHandler(file_handler)
    return log


ARGS = get_arguments()

os.makedirs(TEMP_PATH, exist_ok=True)
os.makedirs(ARGS.output_dir, exist_ok=True)
LOG = get_logger(ARGS.output_dir)
conn = sqlite3.connect(os.path.join(ARGS.output_dir, "enumsubs.db"))

LOG.info(f"Starting script run with args {ARGS}")


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
    required_tools = ["findomain", "subfinder", "amass", "assetfinder", "gau", "httpx"]
    for tool in required_tools:
        check_tool_flag = shutil.which(tool)
        if check_tool_flag is None:
            CONSOLE.print(f"[bold red]{tool} is not installed! Exiting...")
            LOG.error(f"Tool {tool} is not installed")
            exit(1)


def bootstrap_db():
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


def insert_domains(domain_list: list[str]):
    domain_list = list(map(lambda d: (d,), domain_list))
    conn.executemany("INSERT OR IGNORE INTO domains VALUES (?)", domain_list)
    conn.commit()
    LOG.info(f"Starter domains inserted: {domain_list}")


def process_input() -> list[str]:
    if ARGS.file:
        with open(ARGS.file, "r") as handle:
            domains = handle.readlines()
        domains = list(map(lambda d: d.strip(), domains))
    else:
        domains = [ARGS.domain]
    return domains


def get_domains_to_scan() -> list[str]:
    domains = conn.execute("SELECT * FROM domains")
    domains = map(lambda d: d[0], domains)
    return list(domains)


def start_scans(domain_list: list[str]):
    LOG.info("Start scans")
    for target in domain_list:
        do_crtsh_scan(target)
        do_findomain_scan(target)
        do_amass_scan(target)
        do_subfinder_scan(target)
        do_assetfinder_scan(target)


def do_crtsh_scan(target: str):
    LOG.info("Start crtsh scan")
    request_headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0"}
    url = f"https://crt.sh/?q={target}"
    try:
        response = requests.get(url, headers=request_headers, verify=False)
        if not response.status_code == 200:
            LOG.warning(f"Failed to pull results from crt.sh. Status code is {response.status_code}")
            return
        output = response.text
        LOG.info(f"Pulled results from crt.sh with content length {len(output)}")
    except Exception as e:
        LOG.error(f"Exception occurred during request to crt.sh. Error is {e}")
        return

    target = target.replace(".", "\\.")
    subdomain_regex = re.compile(r"[\w][\w\.]*" + target)
    result = re.findall(subdomain_regex, output)
    result = list(set(map(lambda r: (r.strip(),), result)))
    LOG.info(f"Completed crt.sh with {len(result)} unique results")
    conn.executemany("INSERT OR IGNORE INTO rawsubdomains VALUES (?)", result)
    conn.commit()
    LOG.info("Added results of crt.sh to database")


def do_findomain_scan(target: str):
    LOG.info("Start finddomain scan")
    env = {}
    if ARGS.spyse_key:
        env["findomain_spyse_token"] = ARGS.spyse_key
    if ARGS.setrails_key:
        env["findomain_securitytrails_token"] = ARGS.setrails_key

    findomain_cmd = f"findomain -t {target} -u {TEMP_PATH}/{target}.fd"
    if env:
        proc = subprocess.run(findomain_cmd, env=env, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        proc = subprocess.run(findomain_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    LOG.info(f"External process completed: {proc}")

    try:
        with open(f"{TEMP_PATH}/{target}.fd", "r") as handle:
            result = handle.readlines()
        LOG.info(f"Read result of finddomain with {len(result)} lines")
    except FileNotFoundError:
        LOG.warning("Reading result file failed")
        return
    result = list(map(lambda r: (r.strip(),), result))
    conn.executemany("INSERT OR IGNORE INTO rawsubdomains VALUES (?)", result)
    conn.commit()
    LOG.info("Added results of finddomain to database")


def do_amass_scan(target: str):
    LOG.info("Start amass scan")
    amass_cmd = f"amass enum -passive -nocolor -silent -d {target}"
    proc = subprocess.run(amass_cmd, shell=True, stdout=subprocess.DEVNULL)
    LOG.info(f"External process completed: {proc}")
    
    amass_db_cmd = f"amass db -names -d {target}"
    try:
        amass_results = subprocess.check_output(amass_db_cmd, shell=True, stdin=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        LOG.warning(f"Error occured: {e.output} with error code {e.returncode}")
        return
    amass_results = amass_results.decode().splitlines()
    if "No names were discovered" in amass_results:
        LOG.warning("Amass failed to get subdomains. Check your code!")
        return
    amass_results = list(map(lambda r: (r.strip(),), amass_results))
    LOG.info(f"Read result of amass with {len(amass_results)} lines")

    conn.executemany("INSERT OR IGNORE INTO rawsubdomains VALUES (?)", amass_results)
    conn.commit()
    LOG.info("Added results of amass to database")


def do_subfinder_scan(target: str):
    LOG.info("Start subfinder scan")
    subfinder_cmd = f"subfinder -recursive -d {target} -o {TEMP_PATH}/{target}.sf"
    proc = subprocess.run(subfinder_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                          stdin=subprocess.DEVNULL)
    LOG.info(f"External process completed: {proc}")

    try:
        with open(f"{TEMP_PATH}/{target}.sf", "r") as handle:
            result = handle.readlines()
        LOG.info(f"Read result of subfinder with {len(result)} lines")
    except FileNotFoundError:
        LOG.warning("Reading result file failed")
        return
    result = list(map(lambda r: (r.strip(),), result))
    conn.executemany("INSERT OR IGNORE INTO rawsubdomains VALUES (?)", result)
    conn.commit()
    LOG.info("Added results of subfinder to database")


def do_assetfinder_scan(target: str):
    LOG.info("Start assetfinder scan")
    assetfinder_cmd = f"assetfinder --subs-only {target}"
    assetfinder_output = subprocess.check_output(assetfinder_cmd, shell=True, stdin=subprocess.DEVNULL)
    assetfinder_output = assetfinder_output.decode().splitlines()
    assetfinder_output = list(map(lambda r: (r.strip(),), assetfinder_output))
    LOG.info(f"Assetfinder returned {len(assetfinder_output)} results")

    conn.executemany("INSERT OR IGNORE INTO rawsubdomains VALUES (?)", assetfinder_output)
    conn.commit()
    LOG.info("Added results of assetfinder to database")


def do_probing():
    LOG.info("Start probing for live subdomains")
    subdomains = conn.execute("SELECT * FROM rawsubdomains")
    subdomains = list(map(lambda s: s[0], subdomains))
    with open(f"{TEMP_PATH}/unprobed.out", "w") as handle:
        handle.write('\n'.join(subdomains))
    LOG.info(f"Wrote {len(subdomains)} unprobed domains into temp file")
    httpx_cmd = f"httpx -l {TEMP_PATH}/unprobed.out -silent -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; " \
                "rv:55.0) Gecko/20100101 Firefox/55.0' -ports 80,8080,8081,8443,443,7001,3000 -status-code " \
                f"-no-color -follow-redirects -title -websocket -json -o {TEMP_PATH}/httpx_subs.txt"
    proc = subprocess.run(httpx_cmd, shell=True, stdout=subprocess.DEVNULL)
    LOG.info(f"External process completed: {proc}")

    @dataclass_json(undefined=Undefined.EXCLUDE)
    @dataclass
    class HttpxOutput:
        scheme: Optional[str] = None
        port: Optional[int] = None
        url: Optional[str] = None
        title: Optional[str] = None
        statuscode: Optional[int] = field(metadata=config(field_name="status_code"), default=None)
        final_dest: Optional[str] = field(metadata=config(field_name="final_url"), default=None)
        statuscodes: Optional[List[int]] = field(metadata=config(field_name="chain_status_codes"), default=None)

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
    LOG.info(f"Read result of httpx with {len(to_insert)} lines")

    conn.executemany("INSERT OR IGNORE INTO results VALUES (?, ?, ?, ?, ?, ?, ?)", to_insert)
    conn.commit()
    LOG.info("Added results of httpx to database")


def get_waybackurls(domain_list: list[str]):
    LOG.info("Start searching for waybackurls")
    for target in domain_list:
        gau_cmd = f"""bash -c "echo '{target}' | gau --blacklist ttf,woff,svg,png,jpg --o {TEMP_PATH}/{target}.gau" """
        proc = subprocess.run(gau_cmd, shell=True, stdout=subprocess.DEVNULL)
        LOG.info(f"External process completed: {proc}")

        with open(f"{TEMP_PATH}/{target}.gau", "r") as handle:
            result = handle.readlines()
        result = list(map(lambda r: (r.strip(),), result))
        LOG.info(f"Read result of gau with {len(result)} lines")

        conn.executemany("INSERT OR IGNORE INTO waybackurls (waybackurl) VALUES (?)", result)
        conn.commit()
        LOG.info("Added results of gau to database")


def get_screenshot_urls() -> list[str]:
    LOG.info("Start preparing urls for screenshotting")
    urls_without_redirect = conn.execute(
        "SELECT redirectURL FROM results WHERE redirectURL IS NOT NULL AND statuscode = 200 "
        "UNION "
        "SELECT protocol || '://' || domain || ':' || port FROM results WHERE redirectURL IS NULL AND statuscode = 200")
    all_urls = list(map(lambda row: row[0], urls_without_redirect.fetchall()))
    LOG.info(f"Created {len(all_urls)} urls to screenshot")
    return all_urls


def export_results():
    LOG.info("Start exporting output files")
    # master.txt
    results = conn.execute("SELECT protocol, domain, port FROM results WHERE statuscode != 429")
    export_lines = []
    for res in results:
        export_lines.append(f"{res[0]}://{res[1]}:{res[2]}")
    with open(os.path.join(ARGS.output_dir, "master.txt"), "w") as handle:
        handle.write("\n".join(export_lines))
    LOG.info(f"Wrote master.txt file with {len(export_lines)} lines")

    # statuscodes.txt
    results = conn.execute(
        "SELECT protocol, domain, port, statuscode, title, redirectURL FROM results WHERE statuscode != 429")
    export_lines = []
    for res in results:
        export_lines.append(f"{res[0]}://{res[1]}:{res[2]} [{res[3]}] [{res[4]}] [{res[5] or ''}]")
    with open(os.path.join(ARGS.output_dir, "statuscodes.txt"), "w") as handle:
        handle.write("\n".join(export_lines))
    LOG.info(f"Wrote statuscodes.txt file with {len(export_lines)} lines")

    # 403.txt
    results = conn.execute("SELECT protocol, domain, port FROM results WHERE statuscode == 403")
    export_lines = []
    for res in results:
        export_lines.append(f"{res[0]}://{res[1]}:{res[2]}")
    with open(os.path.join(ARGS.output_dir, "403.txt"), "w") as handle:
        handle.write("\n".join(export_lines))
    LOG.info(f"Wrote 403.txt file with {len(export_lines)} lines")

    # wayback.txt
    if ARGS.waybacks:
        results = conn.execute("SELECT DISTINCT waybackurl FROM waybackurls")
        export_lines = list(map(lambda w: w[0], results))
        with open(os.path.join(ARGS.output_dir, "waybacks.txt"), "w") as handle:
            handle.write("\n".join(export_lines))
        LOG.info(f"Wrote waybacks.txt file with {len(export_lines)} lines")

    # screenshot_urls.txt
    export_lines = get_screenshot_urls()
    with open(os.path.join(ARGS.output_dir, "screenshot_urls.txt"), "w") as handle:
        handle.write("\n".join(export_lines))
    LOG.info(f"Wrote screenshot_urls.txt file with {len(export_lines)} lines")


def cleanup():
    LOG.info("Start cleaning up")
    shutil.rmtree(TEMP_PATH)
    LOG.info("Removed the temporary directory")
    conn.execute("DELETE FROM domains")
    conn.commit()
    LOG.info("Cleaned the database")


def main():
    print_banner()
    with CONSOLE.status("") as status:
        check_for_tools()
        CONSOLE.print("[cyan]Tool check done!")
        bootstrap_db()
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
        status.update("[bold yellow]Preparing urls for screenshotting")
        get_screenshot_urls()
        CONSOLE.print("[cyan]Screenshot urls ready!")
        if ARGS.waybacks:
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
