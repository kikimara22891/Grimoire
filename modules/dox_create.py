import os
import requests
import random
import datetime
from colorama import Fore

try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone as ph_timezone
except ImportError:
    phonenumbers = None

try:
    from main import BaseGrimoireModule, RED, WHITE, BODY_COLOR, BEFORE, AFTER, INPUT, INFO, RESET
except ImportError:
    RED, WHITE, BODY_COLOR = Fore.RED, Fore.WHITE, "\033[38;2;255;219;172m"
    BEFORE, AFTER, INPUT, INFO, RESET = f"{RED}[", f"{RED}]", f"{WHITE}?", f"{WHITE}!", "\033[0m"
    class BaseGrimoireModule:
        def __init__(self, mod_id, name, category):
            self.id, self.name, self.category = mod_id, name, category

class Module(BaseGrimoireModule):
    def __init__(self):
        super().__init__(mod_id="11", name="DoxCreate", category="OSINT")

    def _get_time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    def IpInfo(self, ip):
        try:
            r = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
            return r.get("isp", "None"), r.get("org", "None"), r.get("as", "None")
        except: return "None", "None", "None"

    def run(self):
        T = f"{BEFORE}{self._get_time()}{AFTER}"
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"{RED}┌────────────────────────────────────────────────────────┐")
        print(f"{RED}│{WHITE}                TARGET DOSSIER SYSTEM                   {RED}│")
        print(f"{RED}└────────────────────────────────────────────────────────┘")
        
        by = input(f"{T} {INPUT} Doxed By: {BODY_COLOR}")
        reason = input(f"{T} {INPUT} Reason: {BODY_COLOR}")
        p1 = input(f"{T} {INPUT} Target Alias: {BODY_COLOR}")

        print(f"\n{RED}[!] {WHITE}TELEGRAM DATA")
        tg_user = input(f"{T} {INPUT} Username: {BODY_COLOR}")
        tg_id = input(f"{T} {INPUT} ID: {BODY_COLOR}")
        tg_phone = input(f"{T} {INPUT} Phone Number: {BODY_COLOR}")
        tg_bio = input(f"{T} {INPUT} Bio/Description: {BODY_COLOR}")

        print(f"\n{RED}[!] {WHITE}DISCORD DATA")
        ds_user = input(f"{T} {INPUT} Username: {BODY_COLOR}")
        ds_id = input(f"{T} {INPUT} ID: {BODY_COLOR}")
        ds_token = input(f"{T} {INPUT} Token: {BODY_COLOR}")
        ds_mail = input(f"{T} {INPUT} Discord Email: {BODY_COLOR}")

        print(f"\n{RED}[!] {WHITE}PC & NETWORK")
        ip_pub = input(f"{T} {INPUT} Public IP: {BODY_COLOR}")
        ip_loc = input(f"{T} {INPUT} Local IP: {BODY_COLOR}")
        pc_name = input(f"{T} {INPUT} PC Name: {BODY_COLOR}")
        isp, org, asn = self.IpInfo(ip_pub)

        print(f"\n{RED}[!] {WHITE}PERSONAL & FAMILY")
        fname = input(f"{T} {INPUT} First Name: {BODY_COLOR}")
        lname = input(f"{T} {INPUT} Last Name: {BODY_COLOR}")
        moth = input(f"{T} {INPUT} Mother: {BODY_COLOR}")
        fath = input(f"{T} {INPUT} Father: {BODY_COLOR}")
        bro = input(f"{T} {INPUT} Brother: {BODY_COLOR}")
        sis = input(f"{T} {INPUT} Sister: {BODY_COLOR}")

        print(f"\n{RED}[!] {WHITE}DOCUMENTS")
        pass_n = input(f"{T} {INPUT} Passport No: {BODY_COLOR}")
        car_n = input(f"{T} {INPUT} Car Plate: {BODY_COLOR}")
        car_v = input(f"{T} {INPUT} VIN: {BODY_COLOR}")

        filename = input(f"\n{T} {INPUT} Save as: {BODY_COLOR}").strip() or f"Dox_{random.randint(100,999)}"
        out_dir = os.path.join(os.getcwd(), "1-Output", "DoxCreate")
        if not os.path.exists(out_dir): os.makedirs(out_dir)
        filepath = os.path.join(out_dir, f"{filename}.txt")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"""
                                            
                  .:+*#%%#####*++++-.             
                :#%%*+*+-.....                    
             .=%%+++:..                           
           .=%#++=.                               
          -%%+++.                                 
      .  =%%++-          ....                     
      #%+#%++=.        .:#%%%*:                   
      :#@%#+=          :*+:-*%#:                  
       .*@@#.         .-%*::-%%#.                 
        .-%@@%-.      .=%%--%%%-                  
          .:--=*+-:.:-#%%%%%%%%*.                      ██████╗   ██████╗  ██╗  ██╗
               .:-*#%%%%%%%%%%%%%-                     ██╔══██╗ ██╔═══██╗ ╚██╗██╔╝
                  .+%%%*+*%%%%%%%%+...                 ██║  ██║ ██║   ██║  ╚███╔╝ 
                  .+%@@%%%%*#%%%%%%%%%*-.              ██║  ██║ ██║   ██║  ██╔██╗
                   .*%@%%%%%%%%%%%%%%%%%#-.            ██████╔╝ ╚██████╔╝ ██╔╝ ██╗
                   .*%%%%%%%%%%%+#%%%%%%%%%*-.         ╚═════╝   ╚═════╝  ╚═╝  ╚═╝
                  .=%%%%%%%%%%%%@%*%%%%%####=-==  
                  :*%%%%%%%%%%%%%%%*#%%%%#+=-==+  
                 .+=*%#%%%%%%%%%%%%%**%%#+**+-:-  
                .-=::*-%%%%%%%%%%%%###*-*%###+:   
                ...:..%%%%%%%%%%%%%%#:=*+-:.      
                     *%%%%%%%%%%%%%%%%.           
                    :#%%%%%%%%%%%%%%%%+           
                   .*%%%%%%%%%%%%%%%%%#.          
                  .=%%%%%%%%%%%%%%%%%%#:          
                  .+%%%%%%%%%%%%%%%%%%%*.         
                    :+*#%%%@%%%%%%%%%%%%#:.       
                      ..:==+*#%#*=-:.:-+***:.
    
    Doxed By : {by}
    Reason   : {reason}
    Target   : {p1}
    Date     : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    ╔═══════════════════════════════════════════════════════════════════════════════════════╗
    TELEGRAM:
    =====================================================================================
    [+] Username     : {tg_user}
    [+] ID           : {tg_id}
    [+] Phone        : {tg_phone}
    [+] Bio          : {tg_bio}
    ╚═══════════════════════════════════════════════════════════════════════════════════════╝

    ╔═══════════════════════════════════════════════════════════════════════════════════════╗
    DISCORD:
    =====================================================================================
    [+] Username     : {ds_user}
    [+] ID           : {ds_id}
    [+] Token        : {ds_token}
    [+] E-Mail       : {ds_mail}
    ╚═══════════════════════════════════════════════════════════════════════════════════════╝

    ╔═══════════════════════════════════════════════════════════════════════════════════════╗
    INFORMATION:
    =====================================================================================
    +────────────Pc────────────+
    [+] IP Public    : {ip_pub}
    [+] IP Local     : {ip_loc}
    [+] ISP          : {isp} | Org: {org}
    [+] AS           : {asn}
    [+] PC Name      : {pc_name}

    +───────────Personal───────+
    [+] Full Name    : {lname} {fname}
    [+] Mother       : {moth} | Father: {fath}
    [+] Brother      : {bro} | Sister: {sis}

    +──────────Documents───────+
    [+] Passport No  : {pass_n}
    [+] Car Number   : {car_n}
    [+] VIN          : {car_v}
    ╚═══════════════════════════════════════════════════════════════════════════════════════╝
            """)

        print(f"\n{T} {INFO} {WHITE}File saved: {RED}{filename}.txt")
        input(f"{T} {INFO} {WHITE}Press {RED}ENTER{WHITE} to exit...")