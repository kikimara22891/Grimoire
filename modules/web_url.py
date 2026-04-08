import os
import re
import requests
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from colorama import Fore

try:
    from main import BaseGrimoireModule, BODY_COLOR, RED, WHITE
except ImportError:
    RED, WHITE, BODY_COLOR = Fore.RED, Fore.WHITE, "\033[38;2;255;219;172m"
    class BaseGrimoireModule:
        def __init__(self, mod_id, name, category):
            self.id, self.name, self.category = mod_id, name, category

class Module(BaseGrimoireModule):
    def __init__(self):
        super().__init__(mod_id="4", name="Website Url Scanner", category="Network")
        self.all_links = set()
        self.visited_links = set()

    def is_valid_extension(self, url):
        return re.search(r'\.(html|xhtml|php|js|css|asp|aspx|jsp)$', url.lower()) or not re.search(r'\.\w+$', url)

    def extract_links(self, base_url, domain, soup):
        extracted = []
        tags = soup.find_all(['a', 'link', 'script', 'img', 'iframe', 'button', 'form'])
        
        for tag in tags:
            attr = tag.get('href') or tag.get('src') or tag.get('action')
            if attr:
                full_url = urljoin(base_url, attr)
                if full_url not in self.all_links and domain in full_url and self.is_valid_extension(full_url):
                    extracted.append(full_url)
                    self.all_links.add(full_url)
        
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                urls_in_script = re.findall(r'(https?://\S+)', script.string)
                for url in urls_in_script:
                    clean_url = url.replace('"', '').replace("'", "").split(')')[0]
                    if clean_url not in self.all_links and domain in clean_url and self.is_valid_extension(clean_url):
                        extracted.append(clean_url)
                        self.all_links.add(clean_url)
        return extracted

    def print_row(self, url, status_code, c1, c2):
        V = RED + "│"
        u_part = f" {url[:c1-2]}".ljust(c1)
        s_part = f" {status_code}".ljust(c2)
        color = Fore.GREEN if str(status_code) == "200" else RED
        print(f"{V}{BODY_COLOR}{u_part}{RED}│{color}{s_part}{RED}│")

    def scan_url(self, website_url, domain, c1, c2):
        try:
            response = requests.get(website_url, timeout=5, verify=False)
            self.print_row(website_url, response.status_code, c1, c2)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                return self.extract_links(website_url, domain, soup)
        except:
            self.print_row(website_url, "ERROR", c1, c2)
        return []

    def run(self):
        print(f"\n{RED}┌──────────────────────────────────────────┐")
        website_url = input(f"{RED}│ {WHITE}Enter Website URL {RED}> {BODY_COLOR}").strip()
        print(f"{RED}├──────────────────────────────────────────┤")
        print(f"{RED}│ {WHITE}[01] Only URL     {RED}│ {WHITE}[02] Full Website {RED}│")
        print(f"{RED}└──────────────────────────────────────────┘")
        choice = input(f"{RED}Grimoire {WHITE}> {BODY_COLOR}").strip()

        if not website_url: return
        if not website_url.startswith(("http://", "https://")):
            website_url = "https://" + website_url
            
        domain = urlparse(website_url).netloc
        os.system('cls' if os.name == 'nt' else 'clear')

        art = [
            "  :::       ::: :::::::::: :::::::::      ::::::::  ",
            "  :+:       :+: :+:        :+:    :+:    :+:    :+: ",
            "  +:+       +:+ +:+        +:+    +:+    +:+        ",
            "  +#+  +:+  +#+ +#++:++#   +#++:++#+     +#++:++#++ ",
            "  +#+ +#+#+ +#+ +#+        +#+    +#+           +#+ ",
            "   #+#+# #+#+#  #+         #+#    #+#    #+#    #+# ",
            "    ###   ###   ########## #########      ########  "
        ]
        for line in art: print(RED + line)

        c1, c2 = 55, 12
        V = RED + "│"
        print(f"\n{RED}[*] {WHITE}SCANNING: {BODY_COLOR}{domain}\n")
        print(RED + "┌" + "─"*c1 + "┬" + "─"*c2 + "┐")
        print(V + WHITE + " EXTRACTED URL".ljust(c1) + RED + "│" + WHITE + " STATUS".ljust(c2) + V)
        print(RED + "├" + "─"*c1 + "┼" + "─"*c2 + "┤")

        self.all_links.add(website_url)
        
        if choice in ['1', '01']:
            self.scan_url(website_url, domain, c1, c2)
        else:
            to_visit = [website_url]
            while to_visit:
                current = to_visit.pop(0)
                if current not in self.visited_links:
                    self.visited_links.add(current)
                    new_found = self.scan_url(current, domain, c1, c2)
                    for link in new_found:
                        if link not in self.visited_links:
                            to_visit.append(link)
                if len(self.visited_links) > 50: break # Safety limit

        print(RED + "└" + "─"*c1 + "┴" + "─"*c2 + "┘")
        self.all_links.clear()
        self.visited_links.clear()