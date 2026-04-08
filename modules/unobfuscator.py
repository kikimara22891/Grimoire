import os
import base64
import zlib
import re
import random
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
        super().__init__(mod_id="20", name="Deobfuscator (Standard)", category="Utilities")
        self.output_dir = os.path.join("1-Output", "Deobfuscated")
        if not os.path.exists(self.output_dir): os.makedirs(self.output_dir)

    def deobfuscate_py_b64(self, code):
        data = re.search(r'b64decode\s*\(\s*["\'](.+?)["\']\s*\)', code).group(1)
        return base64.b64decode(data).decode('utf-8')

    def deobfuscate_py_zlib(self, code):
        data = re.search(r'base64\.b64decode\s*\(\s*["\'](.+?)["\']\s*\)', code).group(1)
        compressed = base64.b64decode(data)
        return zlib.decompress(compressed).decode('utf-8')

    def deobfuscate_py_reverse(self, code):
        data = re.search(r'exec\s*\(\s*["\'](.+?)["\']\s*\[::-1\]\)', code).group(1)
        return data[::-1]

    def run(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{RED}┌────────────────────────────────────────────────────────────┐")
        print(f"{RED}│{WHITE}            DEOBFUSCATOR - REVERSING TOOL                   {RED}│")
        print(f"{RED}└────────────────────────────────────────────────────────────┘")
        print(f"{RED}[!] {WHITE}Paste the obfuscated code line:")
        
        target_code = input(f"{RED} > {BODY_COLOR}").strip()
        if not target_code: return

        try:
            if "zlib" in target_code:
                result = self.deobfuscate_py_zlib(target_code)
                method = "Zlib"
            elif "b64decode" in target_code:
                result = self.deobfuscate_py_b64(target_code)
                method = "Base64"
            elif "[::-1]" in target_code:
                result = self.deobfuscate_py_reverse(target_code)
                method = "Reverse"
            else:
                print(f"{RED}[!] Unknown format.")
                input()
                return

            print(f"\n{RED}[*] {WHITE}Method: {BODY_COLOR}{method}")
            print(f"{RED}┌" + "─"*60 + "┐")
            print(f"{RED}│ {BODY_COLOR}{result[:58].ljust(59)}{RED}│")
            print(f"{RED}└" + "─"*60 + "┘")

            out_file = os.path.join(self.output_dir, f"restored_{random.randint(100,999)}.py")
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"{RED}[✓] Saved to: {BODY_COLOR}{out_file}")

        except Exception as e:
            print(f"{RED}[!] Error: {e}")
