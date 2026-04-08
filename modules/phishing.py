import os
import re
import requests
import datetime
import concurrent.futures
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
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
        super().__init__(mod_id="16", name="Phishing Attack", category="Utilities")
        self.c1, self.c2 = 30, 45
        self.output_dir = os.path.join("1-Output", "PhishingAttack")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def print_row(self, key, value, color=Fore.WHITE):
        V = RED + "│"
        k_part = f" {key}".ljust(self.c1)
        v_part = f" {value}".ljust(self.c2)
        print(f"{V}{BODY_COLOR}{k_part}{RED}│{color}{v_part}{RED}│")

    def fetch_assets(self, urls):
        all_content = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(requests.get, url, timeout=5): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    res = future.result()
                    if res.status_code == 200:
                        res.encoding = res.apparent_encoding
                        all_content.append(res.text)
                except: pass
        return all_content

    def run(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"{RED}┌──────────────────────────────────────────┐")
        url_input = input(f"{RED}│ {WHITE}Enter Website URL {RED}> {BODY_COLOR}").strip()
        print(f"{RED}└──────────────────────────────────────────┘")
        
        if not url_input: return
        target_url = f"https://{url_input}" if not urlparse(url_input).scheme else url_input

        art = [
            "  :::::::::  :::    ::: ::::::::::: ::::::::  :::    ::: ",
            "  :+:    :+: :+:    :+:     :+:    :+:    :+: :+:    :+: ",
            "  +:+    +:+ +:+    +:+     +:+    +:+        +:+    +:+ ",
            "  +#++:++#+  +#++:++#++     +#+    +#++:++#++ +#++:++#++ ",
            "  +#+        +#+    +#+     +#+           +#+ +#+    +#+ ",
            "  #+#        #+#    #+#     +#+    #+#    #+# #+#    #+# ",
            "  ###        ###    ### ########### ########  ###    ### "
        ]
        for line in art: print(RED + line)

        print(f"\n{RED}[*] {WHITE}CLONING TARGET: {BODY_COLOR}{target_url}\n")
        
        print(RED + "┌" + "─"*self.c1 + "┬" + "─"*self.c2 + "┐")
        print(RED + "│" + WHITE + " PROCESS STEP".ljust(self.c1) + RED + "│" + WHITE + " STATUS".ljust(self.c2) + RED + "│")
        print(RED + "├" + "─"*self.c1 + "┼" + "─"*self.c2 + "┤")

        try:
            res = requests.get(target_url, timeout=10)
            if res.status_code != 200:
                self.print_row("HTTP Connection", "FAILED", RED)
                return

            res.encoding = res.apparent_encoding
            
            soup = BeautifulSoup(res.text, 'html.parser')
            self.print_row("HTML Recovery", "SUCCESS (UTF-8)", Fore.GREEN)


            css_tags = soup.find_all('link', rel='stylesheet')
            css_urls = [urljoin(target_url, t['href']) for t in css_tags if t.has_attr('href')]
            css_data = self.fetch_assets(css_urls)
            
            style_tag = soup.new_tag('style')
            style_tag.string = "\n".join(css_data)
            if soup.head: soup.head.append(style_tag)
            for t in css_tags: t.decompose()
            self.print_row("CSS Inlining", f"LOADED {len(css_data)} FILES", Fore.CYAN)


            js_tags = soup.find_all('script', src=True)
            js_urls = [urljoin(target_url, t['src']) for t in js_tags if t.has_attr('src')]
            js_data = self.fetch_assets(js_urls)

            script_tag = soup.new_tag('script')
            script_tag.string = "\n".join(js_data)
            if soup.body: soup.body.append(script_tag)
            for t in js_tags: t.decompose()
            self.print_row("JS Inlining", f"LOADED {len(js_data)} FILES", Fore.CYAN)


            title = re.sub(r'[\\/:*?"<>|]', '-', soup.title.string if soup.title else 'Phishing_Clone')
            file_name = f"{title}.html"
            file_path = os.path.join(self.output_dir, file_name)


            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(soup.prettify(formatter="html"))

            self.print_row("Output File", file_name[:self.c2-2])
            self.print_row("Attack Readiness", "CLONE READY", Fore.GREEN)

        except Exception as e:
            self.print_row("Error", "Critical failure", RED)

        print(RED + "└" + "─"*self.c1 + "┴" + "─"*self.c2 + "┘")
        print(f"\n{RED}[!] {WHITE}Location: {BODY_COLOR}{self.output_dir}")