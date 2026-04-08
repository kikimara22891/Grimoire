import os
import platform
import subprocess
import time
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
        super().__init__(mod_id="3", name="ICMP Pinger", category="Network")

    def run(self):
        print(f"\n{RED}┌──────────────────────────────────────────┐")
        target = input(f"{RED}│ {WHITE}Enter Target IP/Host {RED}> {BODY_COLOR}").strip()
        count_input = input(f"{RED}│ {WHITE}Packets Count        {RED}> {BODY_COLOR}").strip()
        timeout_input = input(f"{RED}│ {WHITE}Timeout (ms)         {RED}> {BODY_COLOR}").strip()
        print(f"{RED}└──────────────────────────────────────────┘")
        
        if not target: return
        
        try:
            # Никаких min(..., 20), берем сколько ввел юзер
            max_pings = int(count_input) if count_input else 4
            ms_timeout = int(timeout_input) if timeout_input else 1000
        except:
            max_pings, ms_timeout = 4, 1000

        os.system('cls' if os.name == 'nt' else 'clear')

        art = [
            "  :::::::::  ::::::::::: ::::    :::  ::::::::  ",
            "  :+:    :+:     :+:     :+:+:   :+: :+:    :+: ",
            "  +:+    +:+     +:+     :+:+:+  +:+ +:+        ",
            "  +#++:++#+      +#+     +#+ +:+ +#+ :#:        ",
            "  +#+            +#+     +#+  +#+#+# +#+   +#+# ",
            "  ###        ########### ###   ####  ########## "
        ]
        for line in art:
            print(RED + line)

        print(f"\n{RED}[*] {WHITE}PINGING TARGET: {BODY_COLOR}{target}\n")

        c1, c2, c3 = 30, 12, 18
        V = RED + "│"
        
        print(RED + "┌" + "─"*c1 + "┬" + "─"*c2 + "┬" + "─"*c3 + "┐")
        print(V + (WHITE + " TARGET").ljust(c1+5) + RED + "│" + (WHITE + " MS").ljust(c2+5) + RED + "│" + (WHITE + " STATUS").ljust(c3+5) + V)
        print(RED + "├" + "─"*c1 + "┼" + "─"*c2 + "┼" + "─"*c3 + "┤")

        param = "-n" if platform.system().lower() == "windows" else "-c"
        timeout_param = "-w" if platform.system().lower() == "windows" else "-W"
        actual_timeout = str(ms_timeout) if platform.system().lower() == "windows" else str(max(1, ms_timeout // 1000))

        consecutive_fails = 0

        try:
            for i in range(max_pings):
                try:
                    start_time = time.time()
                    process = subprocess.run(
                        ["ping", param, "1", timeout_param, actual_timeout, target],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True
                    )
                    end_time = time.time()
                    latency = f"{int((end_time - start_time) * 1000)}ms"
                    
                    if process.returncode == 0:
                        st_text, st_color = "ONLINE", Fore.GREEN
                        ms_text = latency
                        consecutive_fails = 0
                    else:
                        st_text, st_color = "TIMEOUT", RED
                        ms_text = "0ms"
                        consecutive_fails += 1
                except:
                    ms_text, st_text, st_color = "0ms", "ERROR", RED
                    consecutive_fails += 1

                t_part = f" {target[:c1-2]}".ljust(c1)
                m_part = f" {ms_text}".ljust(c2)
                s_part = f" {st_text}".ljust(c3)

                print(f"{V}{BODY_COLOR}{t_part}{RED}│{BODY_COLOR}{m_part}{RED}│{st_color}{s_part}{RED}│")
                
                if consecutive_fails >= 20:
                    print(RED + "├" + "─"*c1 + "┼" + "─"*c2 + "┼" + "─"*c3 + "┤")
                    msg = " DEAD HOST: 20 ERRORS IN ROW "
                    print(V + f" {RED}{msg}".ljust(c1 + c2 + c3 + 12) + V)
                    break

                time.sleep(0.01)
        except KeyboardInterrupt:
            pass

        print(RED + "└" + "─"*c1 + "┴" + "─"*c2 + "┴" + "─"*c3 + "┘")