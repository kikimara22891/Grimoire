import os
import random
import time
import requests
import subprocess
from colorama import Fore

try:
    from main import BaseGrimoireModule, RED, WHITE, BODY_COLOR
except ImportError:
    RED, WHITE, BODY_COLOR = Fore.RED, Fore.WHITE, "\033[38;2;255;219;172m"
    class BaseGrimoireModule:
        def __init__(self, mod_id, name, category):
            self.id, self.name, self.category = mod_id, name, category


class Module(BaseGrimoireModule):
    def __init__(self):
        super().__init__("21", "Network Engine", "Utilities")

        self.mode = "direct"  # direct / tor / proxy / rotate
        self.tor_proxy = "socks5h://127.0.0.1:9050"

        self.proxies = []
        self.load_proxies()

    # =========================
    # PROXY LOADER
    # =========================

    def load_proxies(self):
        path = "proxies.txt"
        if os.path.exists(path):
            with open(path, "r") as f:
                self.proxies = [p.strip() for p in f if ":" in p]

    def get_random_proxy(self):
        if not self.proxies:
            return None
        return random.choice(self.proxies)

    # =========================
    # HEADERS
    # =========================

    def random_headers(self):
        uas = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (X11; Linux x86_64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        ]

        return {
            "User-Agent": random.choice(uas),
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
        }

    # =========================
    # BUILD PROXY
    # =========================

    def build_proxy(self):
        if self.mode == "tor":
            return {"http": self.tor_proxy, "https": self.tor_proxy}

        elif self.mode == "proxy":
            p = self.get_random_proxy()
            if p:
                return {"http": f"http://{p}", "https": f"http://{p}"}

        elif self.mode == "rotate":
            p = self.get_random_proxy()
            if p:
                return {"http": f"http://{p}", "https": f"http://{p}"}

        return None

    # =========================
    # CORE REQUEST
    # =========================

    def request(self, url):
        retries = 3

        for _ in range(retries):
            try:
                proxy = self.build_proxy()

                res = requests.get(
                    url,
                    headers=self.random_headers(),
                    proxies=proxy,
                    timeout=10
                )

                # delay
                time.sleep(random.uniform(0.5, 2.0))

                return res

            except:
                continue

        return None

    # =========================
    # TOR CONTROL
    # =========================

    def start_tor(self):
        try:
            subprocess.run(["sudo", "systemctl", "start", "tor"], check=True)
            return True
        except:
            return False

    def check_ip(self):
        try:
            real = requests.get("https://api.ipify.org", timeout=5).text
        except:
            real = "error"

        try:
            tor = requests.get(
                "https://api.ipify.org",
                proxies={"http": self.tor_proxy, "https": self.tor_proxy},
                timeout=5
            ).text
        except:
            tor = "tor error"

        return real, tor

    # =========================
    # UI
    # =========================

    def run(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        print(f"{RED}Network Engine v3{WHITE}")
        print(f"{RED}Mode: {BODY_COLOR}{self.mode}\n")

        menu = [
            "1. Set Mode (direct/tor/proxy/rotate)",
            "2. Test Request",
            "3. Show IP",
            "4. Start Tor",
            "5. Reload Proxies",
            "0. Exit"
        ]

        for m in menu:
            print(BODY_COLOR + m)

        choice = input(f"\n{RED}> {BODY_COLOR}").strip()

        if choice == "1":
            m = input("Mode > ").strip()
            if m in ["direct", "tor", "proxy", "rotate"]:
                self.mode = m

        elif choice == "2":
            url = input("URL > ").strip()
            res = self.request(url)
            if res:
                print(f"{WHITE}[{res.status_code}] {len(res.text)} bytes")
            else:
                print(f"{RED}Request failed")

        elif choice == "3":
            real, tor = self.check_ip()
            print(f"Real IP: {real}")
            print(f"Tor IP:  {tor}")

        elif choice == "4":
            print("Starting Tor...")
            print("OK" if self.start_tor() else "Failed")

        elif choice == "5":
            self.load_proxies()
            print(f"Loaded: {len(self.proxies)} proxies")

        input("\nPress Enter...")