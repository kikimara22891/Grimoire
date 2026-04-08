import os
import datetime
import time
import json
from colorama import Fore

try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone as ph_timezone
except ImportError:
    phonenumbers = None

try:
    import requests
except ImportError:
    requests = None

try:
    from main import BaseGrimoireModule, RED, WHITE, BODY_COLOR
except ImportError:
    RED, WHITE, BODY_COLOR = Fore.RED, Fore.WHITE, "\033[38;2;255;219;172m"
    class BaseGrimoireModule:
        def __init__(self, mod_id, name, category):
            self.id, self.name, self.category = mod_id, name, category

class Module(BaseGrimoireModule):
    def __init__(self):
        super().__init__(mod_id="14", name="Phonenumber Lookup", category="OSINT")
        self.c1, self.c2 = 30, 45
        self.leakcheck_api_key = os.getenv("LEAKCHECK_API_KEY", "")
        self.getcontact_api_key = os.getenv("GETCONTACT_API_KEY", "")

    def print_row(self, key, value, color=Fore.WHITE):
        V = RED + "│"
        k_part = f" {key}".ljust(self.c1)
        v_part = f" {value}".ljust(self.c2)
        print(f"{V}{BODY_COLOR}{k_part}{RED}│{color}{v_part}{RED}│")

    def check_leakcheck(self, phone_number):
        """Check phone number in breach databases via LeakCheck API"""
        if not self.leakcheck_api_key or not requests:
            return []  

        try:
            url = "https://leakcheck.net/api/public"
            params = {
                "key": self.leakcheck_api_key,
                "check": phone_number,
                "type": "phone"
            }
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("found"):
                    leaks = data.get("result", [])
                    return [("LeakCheck", f"Found in {len(leaks)} breach(es)")] + \
                           [(f"  → {leak.get('name','Unknown')}", leak.get('date','N/A')) for leak in leaks[:3]]
                else:
                    return [("LeakCheck", "Not found in known breaches")]
            else:
                return []  
        except Exception as e:
            return []  

    def fetch_getcontact_tags(self, phone_number):
        if not self.getcontact_api_key or not requests:
            return []  

        try:
            url = "https://api.getcontact.com/v2/tags"
            headers = {"Authorization": f"Bearer {self.getcontact_api_key}"}
            params = {"phone": phone_number}
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            if resp.status_code == 200:
                tags = resp.json().get("tags", [])
                if tags:
                    return [("GetContact Tags", ", ".join(tags[:5]))] + \
                           [(f"  Tag #{i+1}", tag) for i, tag in enumerate(tags[:3])]
                else:
                    return [("GetContact Tags", "No tags found")]
            else:
                return []  
        except Exception as e:
            return [] 

    def run(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{RED}┌──────────────────────────────────────────┐")
        print(f"{RED}│{WHITE} Optional API Keys (press Enter to skip)   {RED}│")
        print(f"{RED}├──────────────────────────────────────────┤")
        if not self.leakcheck_api_key:
            key = input(f"{RED}│ {WHITE}LeakCheck API key {RED}[optional]{RED}> {BODY_COLOR}").strip()
            if key:
                self.leakcheck_api_key = key
        if not self.getcontact_api_key:
            key = input(f"{RED}│ {WHITE}GetContact API key {RED}[optional]{RED}> {BODY_COLOR}").strip()
            if key:
                self.getcontact_api_key = key
        print(f"{RED}└──────────────────────────────────────────┘\n")
        
        print(f"{RED}┌──────────────────────────────────────────┐")
        number_input = input(f"{RED}│ {WHITE}Enter Phone Number {RED}> {BODY_COLOR}").strip()
        print(f"{RED}└──────────────────────────────────────────┘")
        
        if not number_input: return

        art = [
            "  :::::::::  :::    :::  ::::::::  ::::    :::  ::::::::: ",
            "  :+:    :+: :+:    :+: :+:    :+: :+:+:   :+:  :+:    :+: ",
            "  +:+    +:+ +:+    +:+ +:+    +:+ :+:+:+  +:+  +:+    +:+ ",
            "  +#++:++#+  +#++:++#++ +#+    +:+ +#+ +:+ +#+  +#++:++#+  ",
            "  +#+        +#+    +#+ +#+    +#+ +#+  +#+#+#  +#+        ",
            "  #+#        #+#    #+# #+#    #+# #+#   #+#+#  #+#        ",
            "  ###        ###    ###  ########  ###    ####  ###        "
        ]
        for line in art: print(RED + line)

        print(f"\n{RED}[*] {WHITE}ANALYZING TARGET: {BODY_COLOR}{number_input}\n")
        
        print(RED + "┌" + "─"*self.c1 + "┬" + "─"*self.c2 + "┐")
        print(RED + "│" + WHITE + " DATA TYPE".ljust(self.c1) + RED + "│" + WHITE + " INFORMATION".ljust(self.c2) + RED + "│")
        print(RED + "├" + "─"*self.c1 + "┼" + "─"*self.c2 + "┤")

        try:
            parsed = phonenumbers.parse(number_input)
            is_valid = phonenumbers.is_valid_number(parsed)
            
            status = "VALID" if is_valid else "INVALID"
            stat_color = Fore.GREEN if is_valid else RED
            self.print_row("Verification Status", status, stat_color)

            if is_valid:
                country = geocoder.description_for_number(parsed, "en")
                operator = carrier.name_for_number(parsed, "en")
                zones = ph_timezone.time_zones_for_number(parsed)
                
                self.print_row("Country", country if country else "N/A")
                self.print_row("Carrier / Operator", operator if operator else "Unknown")
                self.print_row("Timezone", ", ".join(zones) if zones else "N/A")
                
                leaks = self.check_leakcheck(number_input)
                for key, val in leaks:
                    self.print_row(key, val, Fore.YELLOW if "Found" in val else Fore.WHITE)
                
                tags = self.fetch_getcontact_tags(number_input)
                for key, val in tags:
                    self.print_row(key, val, Fore.CYAN)
            else:
                self.print_row("Error", "Number is not active or fake", RED)

        except Exception as e:
            self.print_row("Format Check", "Invalid Format", RED)
            self.print_row("Advice", "Use international format (+7...)")

        print(RED + "└" + "─"*self.c1 + "┴" + "─"*self.c2 + "┘")