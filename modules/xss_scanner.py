import os
import requests
import urllib3
import time
from urllib.parse import urljoin, urlparse
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
        super().__init__(mod_id="7", name="XSS Scanner", category="Web-Vuln")
        self.payloads = [
            "<script>alert(1)</script>",
            "\"><script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "<svg/onload=alert(1)>",
            "{{7*7}}"
        ]

    def _print_row(self, p, pay, stat, col, c1, c2, c3):
        V = RED + "│"
        p_txt = f" {p}"[:c1-1].ljust(c1)
        l_txt = f" {pay}"[:c2-1].ljust(c2)
        s_txt = f" {stat}"[:c3-1].ljust(c3)
        print(f"{V}{BODY_COLOR}{p_txt}{RED}│{BODY_COLOR}{l_txt}{RED}│{col}{s_txt}{RED}│")

    def run(self):

        print(f"\n{RED}┌─────────────────── PAYLOAD LIST ──────────────────┐")
        for i, p in enumerate(self.payloads, 1):
            print(f"{RED}│ {WHITE}{i}. {BODY_COLOR}{p.ljust(45)} {RED}│")
        print(f"{RED}└───────────────────────────────────────────────────┘")

        print(f"{RED}┌──────────────────────────────────────────┐")
        target_url = input(f"{RED}│ {WHITE}URL {RED}> {BODY_COLOR}").strip()
        custom_payload = input(f"{RED}│ {WHITE}USE PAYLOAD {RED}> {BODY_COLOR}").strip()
        print(f"{RED}└──────────────────────────────────────────┘")

        if not target_url: return
        if not target_url.startswith(("http://", "https://")):
            target_url = "https://" + target_url


        active_payloads = [custom_payload] if custom_payload else self.payloads

        os.system('cls' if os.name == 'nt' else 'clear')
        c1, c2, c3 = 25, 25, 25
        V = RED + "│"

        print(f"\n{RED}[*] {WHITE}SCANNING XSS: {BODY_COLOR}{target_url}\n")
        print(RED + "┌" + "─"*c1 + "┬" + "─"*c2 + "┬" + "─"*c3 + "┐")
        print(V + WHITE + " PARAMETER".ljust(c1) + RED + "│" + WHITE + " PAYLOAD".ljust(c2) + RED + "│" + WHITE + " STATUS".ljust(c3) + V)
        print(RED + "├" + "─"*c1 + "┼" + "─"*c2 + "┼" + "─"*c3 + "┤")

        try:
            res = requests.get(target_url, timeout=10, verify=False)
            soup = BeautifulSoup(res.content, 'html.parser')
            

            parsed = urlparse(target_url)
            if parsed.query:
                for param in parsed.query.split('&'):
                    if '=' in param:
                        p_name = param.split('=')[0]
                        for payload in active_payloads:
                            test_url = target_url.replace(param, f"{p_name}={payload}")
                            try:
                                r = requests.get(test_url, timeout=7, verify=False)
                                if payload in r.text:
                                    self._print_row(p_name, payload, "VULNERABLE", Fore.GREEN, c1, c2, c3)
                                else:
                                    self._print_row(p_name, payload, "SECURE", RED, c1, c2, c3)
                            except: pass


            for form in soup.find_all('form'):
                action = form.get('action')
                post_url = urljoin(target_url, action)
                method = form.get('method', 'get').lower()
                for inp in form.find_all(['input', 'textarea']):
                    name = inp.get('name')
                    if not name or inp.get('type') == 'submit': continue
                    for payload in active_payloads:
                        try:
                            data = {name: payload}
                            r = requests.post(post_url, data=data, timeout=7, verify=False) if method == 'post' else requests.get(post_url, params=data, timeout=7, verify=False)
                            
                            if payload in r.text:
                                self._print_row(f"F:{name}", payload, "VULNERABLE", Fore.GREEN, c1, c2, c3)
                            else:
                                self._print_row(f"F:{name}", payload, "SECURE", RED, c1, c2, c3)
                        except: pass
        except: pass
        print(RED + "└" + "─"*c1 + "┴" + "─"*c2 + "┴" + "─"*c3 + "┘")