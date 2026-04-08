import os
import hashlib
import datetime
import time
import threading
import queue
import requests
import itertools
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
        super().__init__(mod_id="17", name="Password Decrypted", category="Utilities")
        self.c1, self.c2 = 30, 45

    def print_row(self, key, value, color=Fore.WHITE):
        V = RED + "│"
        k_part = f" {key}".ljust(self.c1)
        v_part = f" {value}".ljust(self.c2)
        print(f"{V}{BODY_COLOR}{k_part}{RED}│{color}{v_part}{RED}│")


    def identify_hash(self, h):
        h = h.strip().lower()
        l = len(h)

        if l == 32 and all(c in '0123456789abcdef' for c in h):
            return "MD5"

        if l == 40 and all(c in '0123456789abcdef' for c in h):
            return "SHA-1"

        if l == 64 and all(c in '0123456789abcdef' for c in h):
            return "SHA-256"

        if l == 128 and all(c in '0123456789abcdef' for c in h):
            return "SHA-512"

        if l == 32 and all(c in '0123456789ABCDEF' for c in h):
            return "NTLM"

        if l == 60 and h.startswith('$2'):
            return "bcrypt"
        return "Unknown"


    def hash_password(self, password, algo, salt=None):
        password = password.encode('utf-8')
        if salt:
            if salt['position'] == 'prefix':
                data = salt['value'].encode('utf-8') + password
            else:
                data = password + salt['value'].encode('utf-8')
        else:
            data = password

        if algo == "MD5":
            return hashlib.md5(data).hexdigest()
        elif algo == "SHA-1":
            return hashlib.sha1(data).hexdigest()
        elif algo == "SHA-256":
            return hashlib.sha256(data).hexdigest()
        elif algo == "SHA-512":
            return hashlib.sha512(data).hexdigest()
        elif algo == "NTLM":

            import hashlib
            return hashlib.new('md4', password.decode('utf-8').encode('utf-16le')).hexdigest().upper()
        else:
            return None


    def try_online(self, hash_str, algo):
        if algo != "MD5":
            return None
        try:
            url = f"https://md5decrypt.net/en/Api/api.php?hash={hash_str}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200 and "not found" not in resp.text.lower():
                return resp.text.strip()
        except:
            pass

        try:
            url = f"https://crackstation.net/crack.php"
            data = {"hash": hash_str, "submit": "Crack"}
            resp = requests.post(url, data=data, timeout=5)
            if "cracked" in resp.text:
                # парсинг – упрощённо
                lines = resp.text.split('\n')
                for line in lines:
                    if "Result" in line:
                        return line.split(':')[1].strip()
        except:
            pass
        return None


    def brute_force_thread(self, word_queue, result, hash_str, algo, salt, stop_event):
        while not stop_event.is_set():
            try:
                password = word_queue.get(timeout=1)
            except queue.Empty:
                break
            if self.hash_password(password, algo, salt) == hash_str:
                result.append(password)
                stop_event.set()
                break
            word_queue.task_done()


    def run(self):
        os.system('cls' if os.name == 'nt' else 'clear')


        art = [
            "  ::::::::  :::::::::  ::::::::  :::::::::  :::   :::",
            "  :+:    :+: :+:       :+:    :+: :+:    :+: :+:   :+:",
            "  +:+    +:+ +:+       +:+        +:+    +:+  +:+ +:+",
            "  +#+    +:+ +#++:++#  +#+        +#++:++#:    +#++:",
            "  +#+    +#+ +#+       +#+        +#+    +#+    +#+",
            "  #+#    #+# #+#       #+#    #+# #+#    #+#    #+#",
            "  #########  ########## ########  ###    ###    ###"
        ]
        for line in art:
            print(RED + line)

        print(f"\n{RED}[*] {WHITE}PASSWORD DECRYPTED - ADVANCED HASH CRACKER{RED}\n")


        print(f"{RED}┌──────────────────────────────────────────┐")
        hash_input = input(f"{RED}│ {WHITE}Enter Hash (or path to hashes file) {RED}> {BODY_COLOR}").strip()
        print(f"{RED}└──────────────────────────────────────────┘")
        if not hash_input:
            return


        if os.path.isfile(hash_input):
            with open(hash_input, 'r') as f:
                hashes = [line.strip().lower() for line in f if line.strip()]
            print(f"{RED}[*] {WHITE}Loaded {len(hashes)} hashes from file.{BODY_COLOR}")
        else:
            hashes = [hash_input.lower()]


        print(f"{RED}┌──────────────────────────────────────────┐")
        use_online = input(f"{RED}│ {WHITE}Use online lookup (MD5 only)? (y/n) {RED}> {BODY_COLOR}").strip().lower() == 'y'
        print(f"{RED}└──────────────────────────────────────────┘")

        print(f"{RED}┌──────────────────────────────────────────┐")
        wordlist_path = input(f"{RED}│ {WHITE}Path to wordlist (Enter for default small list) {RED}> {BODY_COLOR}").strip()
        print(f"{RED}└──────────────────────────────────────────┘")

        # Загрузка словаря
        common_passwords = []
        if wordlist_path and os.path.exists(wordlist_path):
            with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                common_passwords = [line.strip() for line in f if line.strip()]
            print(f"{RED}[*] {WHITE}Loaded {len(common_passwords)} passwords from {wordlist_path}{BODY_COLOR}")
        else:
            common_passwords = ["123456", "password", "qwerty", "admin", "123456789", "root", "111111", "123123", "abc123", "admin123"]
            print(f"{RED}[!] {WHITE}Using default small dictionary. For better results provide a wordlist.{BODY_COLOR}")

        print(f"{RED}┌──────────────────────────────────────────┐")
        use_salt = input(f"{RED}│ {WHITE}Use salt? (y/n) {RED}> {BODY_COLOR}").strip().lower() == 'y'
        salt = None
        if use_salt:
            salt_value = input(f"{RED}│ {WHITE}Salt value {RED}> {BODY_COLOR}").strip()
            salt_pos = input(f"{RED}│ {WHITE}Salt position (prefix/suffix) {RED}> {BODY_COLOR}").strip().lower()
            salt = {'value': salt_value, 'position': salt_pos if salt_pos in ['prefix','suffix'] else 'prefix'}
        print(f"{RED}└──────────────────────────────────────────┘")

        for current_hash in hashes:
            print(f"\n{RED}[*] {WHITE}Analyzing hash: {BODY_COLOR}{current_hash}\n")

            print(RED + "┌" + "─"*self.c1 + "┬" + "─"*self.c2 + "┐")
            print(RED + "│" + WHITE + " ANALYSIS".ljust(self.c1) + RED + "│" + WHITE + " VALUE / RESULT".ljust(self.c2) + RED + "│")
            print(RED + "├" + "─"*self.c1 + "┼" + "─"*self.c2 + "┤")

            hash_type = self.identify_hash(current_hash)
            self.print_row("Hash Algorithm", hash_type, Fore.CYAN if hash_type != "Unknown" else RED)

            if hash_type == "Unknown":
                self.print_row("Error", "Unsupported hash type", RED)
                print(RED + "└" + "─"*self.c1 + "┴" + "─"*self.c2 + "┘")
                continue

            found_pass = None

            if use_online and hash_type == "MD5":
                self.print_row("Online lookup", "Trying...", Fore.YELLOW)
                online_pass = self.try_online(current_hash, hash_type)
                if online_pass:
                    found_pass = online_pass
                    self.print_row("Online result", f"Found: {online_pass}", Fore.GREEN)

            if not found_pass:
                self.print_row("Wordlist Status", f"Scanning {len(common_passwords)} passwords...")
                # Многопоточный перебор
                word_queue = queue.Queue()
                for pwd in common_passwords:
                    word_queue.put(pwd)

                result_list = []
                stop_event = threading.Event()
                threads = []
                num_threads = min(os.cpu_count(), 8)
                for _ in range(num_threads):
                    t = threading.Thread(target=self.brute_force_thread, args=(word_queue, result_list, current_hash, hash_type, salt, stop_event))
                    t.start()
                    threads.append(t)

                for t in threads:
                    t.join()

                if result_list:
                    found_pass = result_list[0]
                    self.print_row("Attack Status", "SUCCESSFUL", Fore.GREEN)
                    self.print_row("Decrypted Password", found_pass, Fore.GREEN)
                else:
                    self.print_row("Attack Status", "FAILED / NOT IN LIST", RED)
                    self.print_row("Advice", "Try a larger wordlist or use rules/mask attack")

            print(RED + "└" + "─"*self.c1 + "┴" + "─"*self.c2 + "┘")
            if found_pass:

                log_dir = os.path.join("1-Output", "PasswordDecrypted")
                os.makedirs(log_dir, exist_ok=True)
                log_file = os.path.join(log_dir, "cracked.txt")
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"{current_hash}:{found_pass}\n")
                print(f"{RED}[+] {WHITE}Result saved to {BODY_COLOR}{log_file}")

        input(f"\n{RED}[!] Press Enter to return...")