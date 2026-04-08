import os
import platform
import random
import string
import subprocess
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
        super().__init__(mod_id="21", name="Anonymization Tool", category="Utilities")
        self.os_type = platform.system()
        self.output_dir = os.path.join("1-Output", "Anonymizer")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _run_with_sudo(self, cmd):
        try:
            subprocess.run(["sudo"] + cmd, check=True)
            return True, "Executed successfully"
        except Exception as e:
            return False, f"Failed: {e}"

    def _run_windows_admin_cmd(self, cmd):
        return False, f"Run manually as Administrator:\n{cmd}"

    def mac_action(self):
        random_mac = "02:" + ":".join(''.join(random.choices('0123456789abcdef', k=2)) for _ in range(5))
        if self.os_type == "Windows":
            adapter = input(f"{RED}[?] Enter network adapter name (e.g., Ethernet0): {BODY_COLOR}").strip()
            cmd = f'Set-NetAdapter -Name "{adapter}" -MacAddress "{random_mac}"'
            return self._run_windows_admin_cmd(cmd)
        elif self.os_type == "Darwin":
            iface = input(f"{RED}[?] Enter interface (e.g., en0): {BODY_COLOR}").strip()
            return self._run_with_sudo(["ifconfig", iface, "ether", random_mac])
        else:
            iface = input(f"{RED}[?] Enter interface (e.g., wlan0, eth0): {BODY_COLOR}").strip()
            return self._run_with_sudo(["ip", "link", "set", "dev", iface, "address", random_mac])

    def mac_instruction(self):
        random_mac = "02:" + ":".join(''.join(random.choices('0123456789abcdef', k=2)) for _ in range(5))
        if self.os_type == "Windows":
            return f"1. Open PowerShell as Admin\n2. Get-NetAdapter | Format-List Name, InterfaceDescription\n3. Set-NetAdapter -Name \"YOUR_ADAPTER\" -MacAddress \"{random_mac}\""
        elif self.os_type == "Darwin":
            return f"1. Disable interface: sudo ifconfig en0 down\n2. Change MAC: sudo ifconfig en0 ether {random_mac}\n3. Enable: sudo ifconfig en0 up\n(Replace en0 with your interface)"
        else:
            return f"1. sudo ip link set dev wlan0 down\n2. sudo ip link set dev wlan0 address {random_mac}\n3. sudo ip link set dev wlan0 up"

    def hostname_action(self, new_name=None):
        if not new_name:
            new_name = input(f"{RED}[?] Enter new hostname (or Enter for random): {BODY_COLOR}").strip()
            if not new_name:
                new_name = "anon-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        if self.os_type == "Windows":
            cmd = f'Rename-Computer -NewName "{new_name}"'
            return self._run_windows_admin_cmd(cmd)
        elif self.os_type == "Darwin":
            cmds = [
                ["scutil", "--set", "ComputerName", new_name],
                ["scutil", "--set", "LocalHostName", new_name],
                ["scutil", "--set", "HostName", new_name]
            ]
            results = []
            for c in cmds:
                ok, msg = self._run_with_sudo(c)
                results.append(msg)
            return all(r[0] for r in results), "\n".join(results)
        else:
            return self._run_with_sudo(["hostnamectl", "set-hostname", new_name])

    def hostname_instruction(self):
        random_name = "anon-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        if self.os_type == "Windows":
            return f"1. PowerShell as Admin\n2. Rename-Computer -NewName \"{random_name}\"\n3. Restart-Computer"
        elif self.os_type == "Darwin":
            return f"1. sudo scutil --set ComputerName \"{random_name}\"\n2. sudo scutil --set LocalHostName \"{random_name}\"\n3. sudo scutil --set HostName \"{random_name}\""
        else:
            return f"1. sudo hostnamectl set-hostname {random_name}\n2. Edit /etc/hostname and /etc/hosts if needed"

    def dns_action(self):
        if self.os_type == "Windows":
            return self._run_windows_admin_cmd("ipconfig /flushdns")
        elif self.os_type == "Darwin":
            return self._run_with_sudo(["dscacheutil", "-flushcache"])
        else:
            ok, msg = self._run_with_sudo(["systemctl", "restart", "systemd-resolved"])
            if not ok:
                ok, msg = self._run_with_sudo(["resolvectl", "flush-caches"])
            return ok, msg

    def dns_instruction(self):
        if self.os_type == "Windows":
            return "CMD as Admin: ipconfig /flushdns"
        elif self.os_type == "Darwin":
            return "sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder"
        else:
            return "sudo systemctl restart systemd-resolved  OR  sudo resolvectl flush-caches"

    def ua_instruction(self):
        ua = random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Version/17.0 Mobile/15E148 Safari/604.1"
        ])
        return f"Use browser extension or set manually:\n{ua}\n\nFor curl: -A \"{ua}\""


    def anonymity_instruction(self):
        return "Check IP/DNS/WebRTC leaks:\n- https://ipleak.net\n- https://browserleaks.com/ip\n- https://dnsleaktest.com"

    def tor_action(self):
        if self.os_type == "Windows":
            return self._run_windows_admin_cmd("Download and run Tor Browser from torproject.org")
        elif self.os_type == "Darwin":
            try:
                subprocess.run(["brew", "services", "start", "tor"], check=True)
                return True, "Tor started via brew"
            except:
                return False, "Install Tor: brew install tor, then run 'tor'"
        else:
            try:
                subprocess.run(["sudo", "systemctl", "start", "tor"], check=True)
                return True, "Tor service started"
            except:
                return False, "Install Tor: sudo apt install tor, then sudo systemctl start tor"

    def tor_instruction(self):
        if self.os_type == "Windows":
            return "1. Download Tor Browser from torproject.org\n2. Run it, SOCKS5 proxy on 127.0.0.1:9050"
        elif self.os_type == "Darwin":
            return "1. brew install tor\n2. brew services start tor\n3. Proxy: 127.0.0.1:9050"
        else:
            return "1. sudo apt install tor\n2. sudo systemctl start tor\n3. Test: curl --socks5-hostname 127.0.0.1:9050 check.torproject.org/api/ip"


    def _print_table(self, title, rows, wrap_width=110):
        """
        rows: list of strings (menu) or list of tuples (label, text)
        """
        if not rows:
            return
        if isinstance(rows[0], tuple):
            max_label_len = max(len(str(r[0])) for r in rows)
            left_width = max_label_len + 4  
            left_width = max_label_len + 3  
            right_width = wrap_width
            total_width = left_width + right_width + 3
        else:
            total_width = max(len(str(r)) for r in rows) + 4
            if total_width > 120:
                total_width = 120

        print(RED + "┌" + "─" * (total_width - 2) + "┐")
        print(RED + "│" + WHITE + title.center(total_width - 2) + RED + "│")
        print(RED + "├" + "─" * (total_width - 2) + "┤")

        for row in rows:
            if isinstance(row, tuple):
                label, text = row
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if len(line) > right_width - 2:
                        line = line[:right_width - 5] + "..."
                    if i == 0:
                        left_cell = f" {label} ".ljust(left_width)
                        print(RED + "│" + BODY_COLOR + left_cell + RED + "│" + Fore.WHITE + f" {line}".ljust(right_width - 1) + RED + "│")
                    else:
                        left_cell = " " * left_width
                        print(RED + "│" + BODY_COLOR + left_cell + RED + "│" + Fore.WHITE + f" {line}".ljust(right_width - 1) + RED + "│")
            else:
                line = str(row)
                if len(line) > total_width - 4:
                    line = line[:total_width - 7] + "..."
                print(RED + "│ " + BODY_COLOR + line.ljust(total_width - 3) + RED + "│")
        print(RED + "└" + "─" * (total_width - 2) + "┘")

    def _confirm_and_execute(self, instruction, action_func, *args):
        self._print_table("INSTRUCTION", [(self.os_type, instruction)])
        answer = input(f"{RED}[?] Do you want to execute this action automatically? (y/n) {RED}> {BODY_COLOR}").strip().lower()
        if answer == 'y':
            ok, msg = action_func(*args)
            self._print_table("EXECUTION RESULT", [("Status", msg)])
        else:
            print(f"{RED}[!] Skipped.")

    def run(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        menu = [
            "0. FULL AUTO (walk through all steps)",
            "1. Change MAC Address",
            "2. Change Hostname",
            "3. Spoof User-Agent (instruction only)",
            "4. Check Anonymity (instruction only)",
            "5. Flush DNS Cache",
            "6. Setup Tor Proxy"
        ]
        self._print_table("ANONYMIZATION TOOL", menu)
        choice = input(f"{RED}[?] Select [0-6] {RED}> {BODY_COLOR}").strip()

        if choice == "0":
            steps = [
                ("MAC Spoof", self.mac_instruction, self.mac_action),
                ("Hostname", self.hostname_instruction, self.hostname_action),
                ("DNS Flush", self.dns_instruction, self.dns_action),
                ("User-Agent", self.ua_instruction, None),
                ("Anonymity Check", self.anonymity_instruction, None),
                ("Tor Proxy", self.tor_instruction, self.tor_action)
            ]
            for step_name, instr_func, act_func in steps:
                print(f"\n{RED}=== {step_name} ==={WHITE}")
                instr = instr_func()
                self._print_table("INSTRUCTION", [(self.os_type, instr)])
                if act_func:
                    answer = input(f"{RED}[?] Execute {step_name}? (y/n) {RED}> {BODY_COLOR}").strip().lower()
                    if answer == 'y':
                        if step_name == "Hostname":
                            new_name = input(f"{RED}[?] Enter new hostname (Enter for random): {BODY_COLOR}").strip()
                            if not new_name:
                                new_name = "autoanon-" + ''.join(random.choices(string.ascii_lowercase+string.digits, k=6))
                            ok, msg = act_func(new_name)
                        elif step_name == "MAC Spoof":
                            ok, msg = act_func()
                        else:
                            ok, msg = act_func()
                        self._print_table("RESULT", [("Status", msg)])
                else:
                    print(f"{RED}[!] No automatic action for {step_name}, follow instructions.")
                input(f"{RED}[?] Press Enter to continue...{WHITE}")
        elif choice == "1":
            self._confirm_and_execute(self.mac_instruction(), self.mac_action)
        elif choice == "2":
            self._confirm_and_execute(self.hostname_instruction(), self.hostname_action)
        elif choice == "3":
            self._print_table("USER-AGENT SPOOF", [(self.os_type, self.ua_instruction())])
        elif choice == "4":
            self._print_table("ANONYMITY CHECK", [(self.os_type, self.anonymity_instruction())])
        elif choice == "5":
            self._confirm_and_execute(self.dns_instruction(), self.dns_action)
        elif choice == "6":
            self._confirm_and_execute(self.tor_instruction(), self.tor_action)
        else:
            print(f"{RED}[!] Invalid choice")