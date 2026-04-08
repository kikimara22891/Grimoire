import os
import base64
import random
import re
import string
import zlib
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
        super().__init__(mod_id="18", name="Obfuscator", category="Utilities")
        self.c1, self.c2 = 30, 50
        self.output_dir = os.path.join("1-Output", "Obfuscator")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def print_row(self, key, value, color=Fore.WHITE):
        V = RED + "│"
        k_part = f" {key}".ljust(self.c1)
        v_part = f" {value}".ljust(self.c2)
        print(f"{V}{BODY_COLOR}{k_part}{RED}│{color}{v_part}{RED}│")

    def _rename_vars_js(self, code):
        def rand_name():
            return ''.join(random.choices(string.ascii_lowercase, k=8))
        pattern = r'\b(?:var|let|const|function)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        vars_found = set(re.findall(pattern, code))
        for v in vars_found:
            new = rand_name()
            code = re.sub(rf'\b{v}\b', new, code)
        return code

    def _hex_strings_js(self, code):
        def repl(m):
            s = m.group(0)
            if '\\x' in s:
                return s
            if s[0] == '"' and s[-1] == '"':
                inner = s[1:-1]
                return '"' + ''.join(f'\\x{ord(c):02x}' for c in inner) + '"'
            if s[0] == "'" and s[-1] == "'":
                inner = s[1:-1]
                return "'" + ''.join(f'\\x{ord(c):02x}' for c in inner) + "'"
            return s
        return re.sub(r'(["\'])(?:(?=(\\?))\2.)*?\1', repl, code)

    def obfuscate_js(self, code, level):
        if level == 1:  
            return self._rename_vars_js(code)
        elif level == 2:  
            code = self._rename_vars_js(code)
            return self._hex_strings_js(code)
        return code

    def obfuscate_py(self, code, method):
        if method == 1:  # b64exec
            b64 = base64.b64encode(code.encode()).decode()
            return f'exec(__import__("base64").b64decode("{b64}"))'
        elif method == 2:  # zlibexec
            comp = zlib.compress(code.encode())
            b64 = base64.b64encode(comp).decode()
            return f'import zlib,base64;exec(zlib.decompress(base64.b64decode("{b64}")))'
        elif method == 3:  # reverse
            return f'exec("{code[::-1]}"[::-1])'
        return code

    def obfuscate_ps(self, code):
        b64 = base64.b64encode(code.encode('utf-16le')).decode()
        return f'powershell.exe -EncodedCommand {b64}'

    def obfuscate_string(self, s, method):
        if method == 1:  # hex
            return ''.join(f'\\x{ord(c):02x}' for c in s)
        elif method == 2:  # base64
            return base64.b64encode(s.encode()).decode()
        elif method == 3:  # rot13
            return s.encode('rot13').decode()
        elif method == 4:  # xor
            key = random.randint(1, 255)
            enc = bytes([ord(c) ^ key for c in s])
            return f'[xor key={key}] {base64.b64encode(enc).decode()}'
        return s

    def generate_xss(self, script, context):
        if context == 1:
            return f'<img src=x onerror="{script}">'
        elif context == 2:
            return f'" onmouseover="{script}"'
        elif context == 3:
            return f'javascript:{script}'
        return script

    def run(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{RED}┌────────────────────────────────────────────────────────────┐")
        print(f"{RED}│{WHITE}            OBFUSCATOR TOOL - Reversible                 {RED}│")
        print(f"{RED}├────────────────────────────────────────────────────────────┤")
        print(f"{RED}│{BODY_COLOR} 1. JavaScript Obfuscation                           {RED}│")
        print(f"{RED}│{BODY_COLOR} 2. Python Obfuscation                              {RED}│")
        print(f"{RED}│{BODY_COLOR} 3. PowerShell Obfuscation                          {RED}│")
        print(f"{RED}│{BODY_COLOR} 4. String Obfuscation                              {RED}│")
        print(f"{RED}│{BODY_COLOR} 5. XSS Payload Generator                           {RED}│")
        print(f"{RED}└────────────────────────────────────────────────────────────┘")
        choice = input(f"{RED}[?] Select [1-5] {RED}> {BODY_COLOR}").strip()

        if choice == "1":
            print(f"{RED}[*] JS Obfuscation (file or paste)")
            src = input(f"{RED}[?] Path to .js file or raw code {RED}> {BODY_COLOR}").strip()
            if os.path.isfile(src):
                with open(src, 'r', encoding='utf-8') as f:
                    code = f.read()
            else:
                code = src
            print(f"{RED}[?] Level: (1) low  (2) medium")
            lvl = input(f"{RED}> {BODY_COLOR}").strip()
            lvl = int(lvl) if lvl.isdigit() and lvl in ['1','2'] else 1
            result = self.obfuscate_js(code, lvl)

        elif choice == "2":
            print(f"{RED}[*] Python Obfuscation")
            src = input(f"{RED}[?] Path to .py file or raw code {RED}> {BODY_COLOR}").strip()
            if os.path.isfile(src):
                with open(src, 'r', encoding='utf-8') as f:
                    code = f.read()
            else:
                code = src
            print(f"{RED}[?] Method: (1) b64exec  (2) zlibexec  (3) reverse")
            m = input(f"{RED}> {BODY_COLOR}").strip()
            m = int(m) if m.isdigit() and m in ['1','2','3'] else 1
            result = self.obfuscate_py(code, m)

        elif choice == "3":
            print(f"{RED}[*] PowerShell Obfuscation")
            src = input(f"{RED}[?] Path to .ps1 file or raw code {RED}> {BODY_COLOR}").strip()
            if os.path.isfile(src):
                with open(src, 'r', encoding='utf-8') as f:
                    code = f.read()
            else:
                code = src
            result = self.obfuscate_ps(code)

        elif choice == "4":
            print(f"{RED}[*] String Obfuscation")
            s = input(f"{RED}[?] String to obfuscate {RED}> {BODY_COLOR}").strip()
            print(f"{RED}[?] Method: (1) hex  (2) base64  (3) rot13  (4) xor")
            m = input(f"{RED}> {BODY_COLOR}").strip()
            m = int(m) if m.isdigit() and m in ['1','2','3','4'] else 1
            result = self.obfuscate_string(s, m)

        elif choice == "5":
            print(f"{RED}[*] XSS Payload Generator")
            script = input(f"{RED}[?] JS script (e.g. alert(1)) {RED}> {BODY_COLOR}").strip()
            print(f"{RED}[?] Context: (1) html  (2) attribute  (3) js")
            ctx = input(f"{RED}> {BODY_COLOR}").strip()
            ctx = int(ctx) if ctx.isdigit() and ctx in ['1','2','3'] else 1
            result = self.generate_xss(script, ctx)

        else:
            print(f"{RED}[!] Invalid choice")
            return


        print(f"\n{RED}┌" + "─"*self.c1 + "┬" + "─"*self.c2 + "┐")
        print(f"{RED}│{WHITE} RESULT".ljust(self.c1) + RED + "│" + WHITE + " OBFUSCATED OUTPUT".ljust(self.c2) + RED + "│")
        print(f"{RED}├" + "─"*self.c1 + "┼" + "─"*self.c2 + "┤")
        lines = result.split('\n')
        for i, line in enumerate(lines[:10]):
            self.print_row(f"Line {i+1}" if i==0 else "", line[:self.c2-2])
        if len(lines) > 10:
            self.print_row("...", f"(+{len(lines)-10} more lines)", Fore.YELLOW)
        print(f"{RED}└" + "─"*self.c1 + "┴" + "─"*self.c2 + "┘")

        out_file = os.path.join(self.output_dir, f"obfuscated_{choice}_{random.randint(1000,9999)}.txt")
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"{RED}[✓] Saved to: {BODY_COLOR}{out_file}")