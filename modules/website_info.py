import os
import re
import ssl
import socket
import requests
import urllib3
import concurrent.futures
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from colorama import Fore

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from main import BaseGrimoireModule, BODY_COLOR, RED, WHITE
except ImportError:
    RED, WHITE, BODY_COLOR = Fore.RED, Fore.WHITE, "\033[38;2;255;219;172m"
    class BaseGrimoireModule:
        def __init__(self, mod_id, name, category):
            self.id, self.name, self.category = mod_id, name, category

class Module(BaseGrimoireModule):
    def __init__(self):
        super().__init__(mod_id="5", name="Website Scanner", category="Network")
        self.c1, self.c2 = 30, 45

    def print_row(self, key, value, color=Fore.WHITE):
        V = RED + "│"
        k_part = f" {key}".ljust(self.c1)
        v_part = f" {value}".ljust(self.c2)
        print(f"{V}{BODY_COLOR}{k_part}{RED}│{color}{v_part}{RED}│")

    def scan_ports(self, ip):
        ports = {
            21: "FTP", 22: "SSH", 80: "HTTP", 443: "HTTPS", 
            3306: "MySQL", 3389: "RDP", 8080: "Proxy"
        }
        open_ports = []
        def check(p):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    if s.connect_ex((ip, p)) == 0:
                        return f"{p}({ports[p]})"
            except: pass
            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(check, ports.keys())
            open_ports = [r for r in results if r]
        return ", ".join(open_ports) if open_ports else "None"

    def run(self):
        print(f"\n{RED}┌──────────────────────────────────────────┐")
        url_input = input(f"{RED}│ {WHITE}Enter Website URL {RED}> {BODY_COLOR}").strip()
        print(f"{RED}└──────────────────────────────────────────┘")
        
        if not url_input: return
        website_url = f"https://{url_input}" if not urlparse(url_input).scheme else url_input
        domain = urlparse(website_url).netloc
        
        os.system('cls' if os.name == 'nt' else 'clear')

        art = [
            "  ::::::::  ::::::::  :::::::::  ::::    ::: ",
            " :+:    :+::+:    :+: :+:    :+: :+:+:   :+: ",
            " +:+       +:+    +:+ +:+    +:+ :+:+:+  +:+ ",
            " +#++:++#++#+    +:+ +#++:++#+  +#+ +:+ +#+ ",
            "        +#++#+    +#+ +#+    +#+ +#+  +#+#+# ",
            " #+#    #+##+#    #+# #+#    #+# #+#   #+#+# ",
            "  ########  ########  ###    ### ###    #### "
        ]
        for line in art: print(RED + line)

        print(f"\n{RED}[*] {WHITE}SCANNING TARGET: {BODY_COLOR}{domain}\n")
        print(RED + "┌" + "─"*self.c1 + "┬" + "─"*self.c2 + "┐")
        print(RED + "│" + WHITE + " DATA TYPE".ljust(self.c1) + RED + "│" + WHITE + " INFORMATION".ljust(self.c2) + RED + "│")
        print(RED + "├" + "─"*self.c1 + "┼" + "─"*self.c2 + "┤")


        try:
            ip = socket.gethostbyname(domain)
            ip_type = "IPv6" if ":" in ip else "IPv4"
        except:
            ip, ip_type = "Unknown", "Unknown"

        self.print_row("Target URL", website_url[:self.c2-2])
        self.print_row("IP Address", ip)
        self.print_row("IP Type", ip_type)


        try:
            api = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5).json()
            self.print_row("ISP / Org", f"{api.get('isp', 'N/A')} / {api.get('org', 'N/A')}"[:self.c2-2])
            self.print_row("Location", f"{api.get('city')}, {api.get('country')}")
        except: pass


        try:
            res = requests.get(website_url, timeout=5, verify=False)
            self.print_row("Status Code", str(res.status_code), Fore.GREEN if res.status_code == 200 else RED)
            self.print_row("Server", res.headers.get('Server', 'Hidden'))
            

            sec_headers = ['Content-Security-Policy', 'Strict-Transport-Security', 'X-Frame-Options']
            for h in sec_headers:
                status = "PROTECTED" if h in res.headers else "MISSING"
                color = Fore.GREEN if status == "PROTECTED" else RED
                self.print_row(h, status, color)


            soup = BeautifulSoup(res.content, 'html.parser')
            techs = []
            if 'jquery' in res.text.lower(): techs.append("jQuery")
            if 'bootstrap' in res.text.lower(): techs.append("Bootstrap")
            if 'wp-content' in res.text.lower(): techs.append("WordPress")
            self.print_row("Technologies", ", ".join(techs) if techs else "None")

        except Exception as e:
            self.print_row("HTTP Scan", "Failed", RED)


        if ip != "Unknown":
            open_p = self.scan_ports(ip)
            self.print_row("Open Ports", open_p, Fore.GREEN if open_p != "None" else RED)

        print(RED + "└" + "─"*self.c1 + "┴" + "─"*self.c2 + "┘")