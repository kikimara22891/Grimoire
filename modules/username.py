import os
import requests
import random
import datetime
import re
import time
from bs4 import BeautifulSoup
from colorama import Fore

try:
    from main import BaseGrimoireModule, RED, WHITE, BODY_COLOR, BEFORE, AFTER, INPUT, INFO, RESET, BEFORE_GREEN, AFTER_GREEN, WAIT, ADD
except ImportError:
    RED, WHITE, BODY_COLOR = Fore.RED, Fore.WHITE, "\033[38;2;255;219;172m"
    BEFORE, AFTER, INPUT, INFO, RESET = f"{RED}[", f"{RED}]", f"{WHITE}?", f"{WHITE}!", "\033[0m"
    BEFORE_GREEN, AFTER_GREEN, WAIT, ADD = f"{Fore.GREEN}[", f"{Fore.GREEN}]", "...", "+"
    class BaseGrimoireModule:
        def __init__(self, mod_id, name, category):
            self.id, self.name, self.category = mod_id, name, category

class Module(BaseGrimoireModule):
    def __init__(self):
        super().__init__(mod_id="12", name="Username Tracker", category="OSINT")
        self.sites = {
            "Telegram": "https://t.me/{}",
            "TikTok": "https://www.tiktok.com/@{}",
            "Instagram": "https://www.instagram.com/{}",
            "GitHub": "https://github.com/{}",
            "Steam": "https://steamcommunity.com/id/{}",
            "YouTube": "https://www.youtube.com/{}",
            "Twitter": "https://twitter.com/{}",
            "Twitch": "https://www.twitch.tv/{}",
            "VK": "https://vk.com/{}",
            "Roblox Trade": "https://rblx.trade/p/{}",
            "Paypal": "https://www.paypal.com/paypalme/{}",
            "Pinterest": "https://www.pinterest.com/{}",
            "Snapchat": "https://www.snapchat.com/add/{}",
            "Spotify": "https://open.spotify.com/user/{}",
            "Reddit": "https://www.reddit.com/user/{}",
            "SoundCloud": "https://soundcloud.com/{}",
            "GitLab": "https://gitlab.com/{}",
            "Linktree": "https://linktr.ee/{}",
            "Xbox": "https://www.xboxgamertag.com/search/{}",
            "Chess.com": "https://www.chess.com/member/{}",
            "Pornhub": "https://rt.pornhub.com/users/{}",
            "Badoo": "https://badoo.com/profile/{}",
            "Fiverr": "https://www.fiverr.com/{}"
        }

    def _get_time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    def SiteException(self, username, site, page_content):
        if site == "Paypal":
            page_content = page_content.replace(f'slug_name={username}', '').replace(f'"slug":"{username}"', '').replace(f'2F{username}&', '')
        elif site == "TikTok":
            page_content = page_content.replace(f'\\u002f@{username}"', '')
        return page_content

    def run(self):
        T = f"{BEFORE}{self._get_time()}{AFTER}"
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"{RED}┌────────────────────────────────────────────────────────┐")
        print(f"{RED}│{WHITE}                SOCIAL USERNAME TRACKER                 {RED}│")
        print(f"{RED}└────────────────────────────────────────────────────────┘")

        username = input(f"\n{T} {INPUT} Enter Username -> {BODY_COLOR}").lower().strip()
        if not username: return

        print(f"{T} {INFO} {WAIT} Scanning {len(self.sites)} platforms...\n")

        number_found = 0
        sites_and_urls_found = []
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

        for site, url_template in self.sites.items():
            try:
                url = url_template.format(username)
                response = session.get(url, timeout=5, allow_redirects=True)
                
                if response.status_code == 200:
                    clean_content = re.sub(r'<[^>]*>', '', response.text.lower().replace(url, "").replace(f"/{username}", ""))
                    clean_content = self.SiteException(username, site, clean_content)

                    soup = BeautifulSoup(response.text, 'html.parser')
                    page_text = soup.get_text().lower().replace(url, "")
                    page_title = soup.title.string.lower() if soup.title else ""

                    if username in page_title or username in clean_content or username in page_text:
                        number_found += 1
                        sites_and_urls_found.append(f"{site}: {url}")
                        print(f"{BEFORE_GREEN}{self._get_time()}{AFTER_GREEN} {WHITE}{site}: {WHITE}{url}")
                    else:
                        print(f"{BEFORE}{self._get_time()}{AFTER} {WHITE}{site}: {RED}Not Found")
                else:
                    print(f"{BEFORE}{self._get_time()}{AFTER} {WHITE}{site}: {RED}Not Found")

            except Exception as e:
                print(f"{BEFORE}{self._get_time()}{AFTER} {RED}{site}: {YELLOW}Failed")

        print(f"\n{T} {INFO} {WHITE}Total Found: {RED}{number_found}")
        print(f"{RED}──────────────────────────────────────────────────────────")
        for item in sites_and_urls_found:
            time.sleep(0.05)
            print(f"{BEFORE_GREEN}{ADD}{AFTER_GREEN} {WHITE}{item}")
        
        print(f"{RED}──────────────────────────────────────────────────────────")