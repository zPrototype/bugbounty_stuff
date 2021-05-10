import re
import subprocess
import argparse
import sqlite3
import os
import shutil
from rich.console import Console

TEMP_PATH = "_tmp"
CONSOLE = Console()

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-d", "--domain", help="Enter a domain you want to scan for subdomains eg. tesla.com")
group.add_argument("-f", "--file", help="Enter a file containing domains you want to scan for subdomains")
parser.add_argument("-sp", "--spyse_key", help="Enter your spyse api key if you have one")
parser.add_argument("-st", "--setrails_key", help="Enter your securitytrails api key if you have one")
args = parser.parse_args()

conn = sqlite3.connect("enumsubs.db")
os.makedirs(TEMP_PATH, exist_ok=True)


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
            port integer,
            statuscode text,
            title text,
            rawstr text,
            unique(domain,port)
        )""")
    conn.execute("CREATE TABLE IF NOT EXISTS waybackurls (waybackurl text unique)")
    conn.commit()


def insert_domains(domain_list):
    domain_list = map(lambda d: (d,), domain_list)
    conn.executemany("INSERT OR IGNORE INTO domains VALUES (?)", domain_list)
    conn.commit()


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
    for target in domain_list:
        do_findomain_scan(target)
        do_sublist3r_scan(target)
        do_subfinder_scan(target)
        do_assetfinder_scan(target)


def do_findomain_scan(target):
    env = {}
    if args.spyse_key:
        env["findomain_spyse_token"] = args.spyse_key
    if args.setrails_key:
        env["findomain_securitytrails_token"] = args.setrails_key

    findomain_cmd = f"findomain -t {target} -u {TEMP_PATH}/{target}.fd"
    if env:
        subprocess.run(findomain_cmd, env=env, shell=True, stdout=subprocess.DEVNULL)
    else:
        subprocess.run(findomain_cmd, shell=True, stdout=subprocess.DEVNULL)

    with open(f"{TEMP_PATH}/{target}.fd", "r") as handle:
        result = handle.readlines()
    result = list(map(lambda r: (r.strip(),), result))
    conn.executemany("INSERT OR IGNORE INTO rawsubdomains VALUES (?)", result)
    conn.commit()


def do_sublist3r_scan(target):
    sublist3r_cmd = f"sublist3r -d {target} -o {TEMP_PATH}/{target}.sl"
    subprocess.run(sublist3r_cmd, shell=True, stdout=subprocess.DEVNULL)

    with open(f"{TEMP_PATH}/{target}.sl", "r") as handle:
        result = handle.readlines()
    result = list(map(lambda r: (r.strip(),), result))
    conn.executemany("INSERT OR IGNORE INTO rawsubdomains VALUES (?)", result)
    conn.commit()


def do_subfinder_scan(target):
    subfinder_cmd = f"subfinder -d {target} -o {TEMP_PATH}/{target}.sf"
    subprocess.run(subfinder_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

    with open(f"{TEMP_PATH}/{target}.sf", "r") as handle:
        result = handle.readlines()
    result = list(map(lambda r: (r.strip(),), result))
    conn.executemany("INSERT OR IGNORE INTO rawsubdomains VALUES (?)", result)
    conn.commit()


def do_assetfinder_scan(target):
    assetfinder_cmd = f"assetfinder --subs-only {target}"
    assetfinder_output = subprocess.check_output(assetfinder_cmd, shell=True, stdin=subprocess.DEVNULL)
    assetfinder_output = assetfinder_output.decode().splitlines()
    assetfinder_output = list(map(lambda r: (r.strip(),), assetfinder_output))

    conn.executemany("INSERT OR IGNORE INTO rawsubdomains VALUES (?)", assetfinder_output)
    conn.commit()


def do_probing():
    subdomains = conn.execute("SELECT * FROM rawsubdomains")
    subdomains = map(lambda s: s[0], subdomains)
    with open(f"{TEMP_PATH}/unprobed.out", "w") as handle:
        handle.write('\n'.join(subdomains))

    httpx_cmd = f"httpx -l {TEMP_PATH}/unprobed.out -silent -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; " \
            "rv:55.0) Gecko/20100101 Firefox/55.0' -ports 80,8080,8081,8443,443,7001,3000 -status-code " \
            f"-no-color -follow-redirects -title -websocket -o {TEMP_PATH}/httpx_subs.txt"
    subprocess.run(httpx_cmd, shell=True, stdout=subprocess.DEVNULL)

    with open(f"{TEMP_PATH}/httpx_subs.txt", "r") as handle:
        probed_subs = handle.readlines()
    httpx_re = re.compile(r"(.*?//)(.*):(\d*) \[(.*)] \[(.*)]")
    to_insert = []
    for sub in probed_subs:
        matched = httpx_re.match(sub)
        to_insert.append((
            matched.group(1),
            matched.group(2),
            int(matched.group(3)),
            matched.group(4),
            matched.group(5),
            matched.group(0)
            ))
    conn.executemany("INSERT OR IGNORE INTO results VALUES (?, ?, ?, ?, ?, ?)", to_insert)
    conn.commit()


def get_waybackurls(domain_list):
    for target in domain_list: 
        gau_cmd = f"""bash -c "echo '{target}' | gau -b ttf,woff,svg,png,jpg -o {TEMP_PATH}/{target}.gau" """
        subprocess.run(gau_cmd, shell=True, stdout=subprocess.DEVNULL)
        
        with open(f"{TEMP_PATH}/{target}.gau", "r") as handle:
            result = handle.readlines()
        result = list(map(lambda r: (r.strip(),), result))
        
        conn.executemany("INSERT OR IGNORE INTO waybackurls VALUES (?)", result)
        conn.commit()


def export_results():
    # master.txt
    results = conn.execute("SELECT protocol, domain, port FROM results WHERE statuscode != 429")
    export_lines = []
    for res in results:
        export_lines.append(f"{res[0]}{res[1]}:{res[2]}")

    with open("master.txt", "w") as handle:
        handle.write("\n".join(export_lines))

    # statuscodes.txt
    results = conn.execute("SELECT rawstr FROM results WHERE statuscode != 429")
    export_lines = map(lambda s: s[0], results)
    with open("statuscodes.txt", "w") as handle:
        handle.write("\n".join(export_lines))

    # 403.txt
    results = conn.execute("SELECT protocol, domain, port FROM results WHERE statuscode == 403")
    export_lines = []
    for res in results:
        export_lines.append(f"{res[0]}{res[1]}:{res[2]}")
    with open("403.txt", "w") as handle:
        handle.write("\n".join(export_lines))

    # wayback.txt
    results = conn.execute("SELECT waybackurl FROM waybackurls")
    export_lines = map(lambda w: w[0], results)
    with open("waybacks.txt", "w") as handle:
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

