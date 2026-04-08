import os
import socket
import sys
import time
from colorama import Fore, Style

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from main import BaseGrimoireModule, BODY_COLOR, RED, WHITE
except ImportError:
    RED, WHITE, BODY_COLOR = Fore.RED, Fore.WHITE, "\033[38;2;255;219;172m"
    class BaseGrimoireModule:
        def __init__(self, mod_id, name, category):
            self.id, self.name, self.category = mod_id, name, category

class Module(BaseGrimoireModule):
    def __init__(self):
        super().__init__(mod_id="2", name="Port Scanner", category="Network")
        self.common_ports = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 
            53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP", 
            443: "HTTPS", 445: "SMB", 1433: "MSSQL", 3306: "MySQL", 
            3389: "RDP", 5432: "PostgreSQL", 8080: "Proxy", 27017: "MongoDB"
        }

    def get_padding(self, text_len):
        try:
            tw = os.get_terminal_size().columns
        except:
            tw = 80
        return " " * max(0, (tw - text_len) // 2)

    def run(self):
        # 1. Запрос цели
        print(f"\n{RED}┌──────────────────────────────────────────┐")
        target = input(f"{RED}│ {WHITE}Enter Target IP/Host {RED}> {BODY_COLOR}").strip()
        print(f"{RED}└──────────────────────────────────────────┘")
        
        if not target: return
        os.system('cls' if os.name == 'nt' else 'clear')

        art = [
            "  :::::::::   ::::::::  :::::::::  :::::::::: ",
            "  :+:    :+: :+:    :+: :+:    :+: :+:        ",
            "  +:+    +:+ +:+    +:+ +:+    +:+ +:+        ",
            "  +#++:++#+  +#+    +:+ +#++:++#:  +#++:++#   ",
            "  +#+        +#+    +#+ +#+    +#+ +#+        ",
            "  ###         ::::::::  ###    ### ########## "
        ]
        for line in art:
            print(self.get_padding(len(line)) + RED + line)

        print("\n" + self.get_padding(40) + f"{WHITE}SCANNING TARGET: {BODY_COLOR}{target}...\n")

        results = []
        for port, service in sorted(self.common_ports.items()):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.4)
            is_open = (s.connect_ex((target, port)) == 0)
            results.append((port, service, is_open))
            s.close()

        w = 46 
        pad = self.get_padding(w + 2)
        V = RED + "│"
        
        # Шапка таблицы
        print(pad + RED + "┌" + "─"*w + "┐")
        print(pad + V + f" SCAN RESULTS: {target} ".center(w) + V)
        print(pad + RED + "├" + "─"*w + "┤")
        
        h_port = "PORT".center(10)
        h_serv = "SERVICE".center(19)
        h_stat = "STATUS".center(15)
        print(pad + V + WHITE + h_port + RED + "│" + WHITE + h_serv + RED + "│" + WHITE + h_stat + V)
        print(pad + RED + "├" + "─"*w + "┤")

        for port, svc, is_open in results:
            status_text = "OPEN" if is_open else "CLOSED"
            st_col = Fore.GREEN if is_open else RED

            p_txt = str(port).center(10)
            s_txt = svc.center(19)
            st_txt = status_text.center(15)

            row = (
                V + 
                BODY_COLOR + p_txt + RED + "│" + 
                BODY_COLOR + s_txt + RED + "│" + 
                st_col + st_txt + V
            )
            print(pad + row)

        # Нижняя граница
        print(pad + RED + "└" + "─"*w + "┘")