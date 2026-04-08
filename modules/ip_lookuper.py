import os
import requests
import socket
import datetime
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
        super().__init__(mod_id="15", name="IP Lookup", category="OSINT")
        self.c1, self.c2 = 30, 45

    def print_row(self, key, value, color=Fore.WHITE):
        V = RED + "│"
        k_part = f" {key}".ljust(self.c1)
        v_part = f" {value}".ljust(self.c2)
        print(f"{V}{BODY_COLOR}{k_part}{RED}│{color}{v_part}{RED}│")

    def is_valid_ip(self, ip):
        try:
            socket.inet_aton(ip)
            return "IPv4"
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET6, ip)
                return "IPv6"
            except socket.error:
                return False

    def run(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"{RED}┌──────────────────────────────────────────┐")
        ip_input = input(f"{RED}│ {WHITE}Enter IP Address {RED}> {BODY_COLOR}").strip()
        print(f"{RED}└──────────────────────────────────────────┘")
        
        if not ip_input: return

        art = [
            "  ::::::::::: :::::::::      :::       ::::::::  :::    ::: ",
            "      :+:     :+:    :+:   :+: :+:    :+:    :+: :+:   :+:  ",
            "      +:+     +:+    +:+  +:+   +:+   +:+        +:+  +:+   ",
            "      +#+     +#++:++#+  +#++:++#++:  +#+        +#++:++    ",
            "      +#+     +#+        +#+     +#+  +#+        +#+  +#+   ",
            "      #+#     #+#        #+#     #+#  #+#    #+# #+#   #+#  ",
            "  ########### ###        ###     ###   ########  ###    ### "
        ]
        for line in art: print(RED + line)

        print(f"\n{RED}[*] {WHITE}SCANNING IP: {BODY_COLOR}{ip_input}\n")
        
        print(RED + "┌" + "─"*self.c1 + "┬" + "─"*self.c2 + "┐")
        print(RED + "│" + WHITE + " DATA TYPE".ljust(self.c1) + RED + "│" + WHITE + " INFORMATION".ljust(self.c2) + RED + "│")
        print(RED + "├" + "─"*self.c1 + "┼" + "─"*self.c2 + "┤")

        ip_version = self.is_valid_ip(ip_input)
        
        if ip_version:
            self.print_row("Validation", "VALID", Fore.GREEN)
            self.print_row("IP Version", ip_version)
            
            try:

                res = requests.get(f"http://ip-api.com/json/{ip_input}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting", timeout=10).json()
                
                if res.get("status") == "success":
                    self.print_row("Country", f"{res.get('country')} ({res.get('countryCode')})")
                    self.print_row("City / Region", f"{res.get('city')}, {res.get('regionName')}")
                    self.print_row("Coordinates", f"{res.get('lat')}, {res.get('lon')}")
                    self.print_row("ISP", res.get("isp"))
                    self.print_row("Organization", res.get("org"))

                    if res.get("hosting"):
                        ip_type = "Hosting / Datacenter"
                        type_color = RED
                    elif res.get("mobile"):
                        ip_type = "Mobile Network"
                        type_color = Fore.CYAN
                    else:
                        ip_type = "Residential (Home)"
                        type_color = Fore.GREEN
                    
                    self.print_row("Connection Type", ip_type, type_color)

                    proxy_status = "DETECTED" if res.get("proxy") else "CLEAN"
                    proxy_color = RED if res.get("proxy") else Fore.GREEN
                    self.print_row("Proxy/VPN Status", proxy_status, proxy_color)
                    self.print_row("Timezone", res.get("timezone"))
                    self.print_row("AS Number", res.get("as"))
                else:
                    self.print_row("API Error", res.get("message", "Unknown error"), RED)
            except Exception as e:
                self.print_row("Scan Error", "Connection failed", RED)
        else:
            self.print_row("Validation", "INVALID", RED)
            self.print_row("Check", "Please enter a correct IP")

        print(RED + "└" + "─"*self.c1 + "┴" + "─"*self.c2 + "┘")