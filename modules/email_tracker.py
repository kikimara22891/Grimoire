import os
import requests
import datetime
import time
import re
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
        super().__init__(mod_id="13", name="Email Tracker", category="OSINT")
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

    def _get_time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    def Instagram(self, email):
        try:
            session = requests.Session()
            h = {'User-Agent': self.ua, 'X-CSRFToken': 'missing', 'Referer': 'https://www.instagram.com/accounts/emailsignup/'}
            r = session.get("https://www.instagram.com/accounts/emailsignup/", headers=h, timeout=5)
            token = session.cookies.get('csrftoken')
            if not token: return False
            h["x-csrftoken"] = token
            r = session.post("https://www.instagram.com/api/v1/web/accounts/web_create_ajax/attempt/", headers=h, data={"email": email}, timeout=5)
            return "email_is_taken" in r.text or "Another account" in r.text
        except: return False

    def Twitter(self, email):
        try:
            r = requests.get("https://api.twitter.com/i/users/email_available.json", params={"email": email}, timeout=5)
            return r.json().get("taken", False)
        except: return False

    def Pinterest(self, email):
        try:
            params = {"source_url": "/", "data": '{"options": {"email": "' + email + '"}, "context": {}}'}
            r = requests.get("https://www.pinterest.com/_ngjs/resource/EmailExistsResource/get/", params=params, timeout=5)
            return r.json()["resource_response"]["data"] is not False
        except: return False

    def Imgur(self, email):
        try:
            session = requests.Session()
            session.get("https://imgur.com/register", timeout=5)
            h = {'User-Agent': self.ua, 'X-Requested-With': 'XMLHttpRequest'}
            r = session.post('https://imgur.com/signin/ajax_email_available', headers=h, data={'email': email}, timeout=5)
            return not r.json()['data']['available']
        except: return False

    def Spotify(self, email):
        try:
            r = requests.get('https://spclient.wg.spotify.com/signup/public/v1/account', params={'validate': '1', 'email': email}, timeout=5)
            return r.json().get("status") == 20
        except: return False

    def FireFox(self, email):
        try:
            r = requests.post("https://api.accounts.firefox.com/v1/account/status", data={"email": email}, timeout=5)
            return "false" not in r.text.lower()
        except: return False

    def run(self):
        T = f"{BEFORE}{self._get_time()}{AFTER}"
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{RED}┌────────────────────────────────────────────────────────┐")
        print(f"{RED}│{WHITE}                  ADVANCED EMAIL TRACKER                {RED}│")
        print(f"{RED}└────────────────────────────────────────────────────────┘")

        email = input(f"\n{T} {INPUT} Enter Email -> {BODY_COLOR}").lower().strip()
        if not email or "@" not in email: return

        print(f"{T} {INFO} {WAIT} Scanning services...\n")
        
        sites = [self.Instagram, self.Twitter, self.Pinterest, self.Imgur, self.Spotify, self.FireFox]
        found_list = []

        for site_func in sites:
            name = site_func.__name__
            if site_func(email):
                found_list.append(name)
                print(f"{BEFORE_GREEN}{self._get_time()}{AFTER_GREEN} {WHITE}{name}: {RED}Found")
            else:
                print(f"{BEFORE}{self._get_time()}{AFTER} {WHITE}{name}: {RED}Not Found")

        print(f"\n{T} {INFO} {WHITE}Total Found: {RED}{len(found_list)}")
        print(f"{RED}──────────────────────────────────────────────────────────")
        for item in found_list:
            time.sleep(0.05)
            print(f"{BEFORE_GREEN}{ADD}{AFTER_GREEN} {WHITE}{item}")
        print(f"{RED}──────────────────────────────────────────────────────────")