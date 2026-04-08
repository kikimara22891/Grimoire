import os
import requests
import urllib3
import pytz
from datetime import datetime
from colorama import Fore

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

RED = Fore.RED
WHITE = Fore.WHITE
BODY = "\033[38;2;255;219;172m"
GREEN = Fore.GREEN

class Module:
    def __init__(self):
        self.id = "1"
        self.name = "IP Scanner"
        self.category = "Network"

    def run(self):
        print(f"\n{RED}┌──────────────────────────────────────────┐")
        target = input(f"{RED}│ {WHITE}Enter IP Address {RED}> {BODY}").strip()
        print(f"{RED}└──────────────────────────────────────────┘")
        
        if not target:
            return

        os.system('cls' if os.name == 'nt' else 'clear')
        
        try:
            r = requests.get(f"http://ip-api.com/json/{target}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,proxy,query", timeout=10).json()
            
            if r.get("status") == "fail":
                print(f"{RED}[!] Error: {r.get('message')}")
                return

            tz_name = r.get('timezone')
            try:
                local_tz = pytz.timezone(tz_name)
                local_time = datetime.now(local_tz).strftime("%H:%M:%S")
                time_info = f"{tz_name} | {local_time}"
            except:
                time_info = f"{tz_name} | Unknown"

            ip_type = "IPv6" if ":" in target else "IPv4"

            print(f"{RED}[*] {WHITE}IP Intelligence: {BODY}{target}\n")
            
            data = [
                ("IP Type", ip_type),
                ("Country", f"{r.get('country')} ({r.get('countryCode')})"),
                ("City/Region", f"{r.get('city')} / {r.get('regionName')}"),
                ("ISP", r.get('isp')),
                ("Lat/Lon", f"{r.get('lat')}, {r.get('lon')}"),
                ("Timezone", time_info),
                ("Proxy/VPN", str(r.get('proxy')))
            ]

            print(f"{RED}┌──────────────┬─────────────────────────────────────────────────────────────────┐")
            print(f"{RED}│ {WHITE}{'DATA TYPE':<12} │ {WHITE}{'INFORMATION':<63} │")
            print(f"{RED}├──────────────┼─────────────────────────────────────────────────────────────────┤")
            for key, val in data:
                print(f"{RED}│ {BODY}{key:<12} {RED}│ {WHITE}{str(val):<63} {RED}│")
            print(f"{RED}└──────────────┴─────────────────────────────────────────────────────────────────┘")

            links = [
                ("Google Maps", f"https://www.google.com/maps?q={r.get('lat')},{r.get('lon')}"),
                ("Whois", f"https://who.is/whois-ip/ip-address/{target}"),
                ("AbuseIPDB", f"https://www.abuseipdb.com/check/{target}")
            ]

            print(f"\n{RED}┌──────────────┬─────────────────────────────────────────────────────────────────┐")
            print(f"{RED}│ {WHITE}{'LINK':<12} │ {WHITE}{'URLs':<63} │")
            print(f"{RED}├──────────────┼─────────────────────────────────────────────────────────────────┤")
            for name, url in links:
                print(f"{RED}│ {BODY}{name:<12} {RED}│ {WHITE}{url[:63]:<63} {RED}│")
            print(f"{RED}└──────────────┴─────────────────────────────────────────────────────────────────┘")

        except Exception as e:
            print(f"{RED}[!] Error: {e}")