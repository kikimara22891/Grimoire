import os
import importlib.util
import numpy as np
from colorama import Fore, Style, init

init(autoreset=True)

RED = Fore.RED
WHITE = Fore.WHITE
BODY_COLOR = "\033[38;2;255;219;172m"


ASCII_ART = [
    "                ##%#######%#%%%                ",
    "             %#%%            %%%%%             ",
    "           %*#%%%:           %%% %#%           ",
    "         ###  %%%###      %#%%%%  #%%          ",
    "        ###    %#  ##%%%%%#  ##     #%         ",
    "        #%     %##  #%#%##  %#       #%        ",
    "       ##       ##%%%    %##%%       %#%       ",
    "       ##      ##%%        #%#%       ##       ",
    "       *#    ###  #%      %%% %#*#    #%       ",
    "       ## ###* %%%    %%%   * #%*###* ",
    "       ##########%%%#%%##%%%%%%##*%##*#        ",
    "        ##          #%  ##=         ##         ",
    "         ###        ### %%         ##:         ",
    "           ##%       %*%%        #%#           ",
    "             ###     %%%      %%##             ",
    "                ##%####%%%%%%%                 "
]

class BaseGrimoireModule:
    def __init__(self, mod_id, name, category="General"):
        self.id = mod_id
        self.name = name
        self.category = category
    def run(self):
        pass

def get_red_gradient(text):
    length = len(text)
    if length <= 1: return RED + text
    red_values = np.linspace(255, 50, length).astype(int)
    return "".join([f"\033[38;2;{red_values[i]};0;0m{char}" for i, char in enumerate(text)]) + Style.RESET_ALL

def load_modules():
    mods = []
    path = "./modules"
    if not os.path.exists(path): os.makedirs(path)
    for f in os.listdir(path):
        if f.endswith(".py") and f != "__init__.py":
            try:
                spec = importlib.util.spec_from_file_location(f[:-3], os.path.join(path, f))
                m_obj = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(m_obj)
                if hasattr(m_obj, 'Module'):
                    mods.append(m_obj.Module())
            except: continue
    return sorted(mods, key=lambda x: int(x.id) if str(x.id).isdigit() else 999)

def render_interface(modules, page=0):
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        tw = os.get_terminal_size().columns
    except:
        tw = 80


    w = 32
    cols_per_page = 3
    
    for line in ASCII_ART:
        print(" " * (tw // 2 - len(line) // 2) + get_red_gradient(line))


    categories = {}
    for m in modules:
        categories.setdefault(m.category, []).append(m)
    cat_names = list(categories.keys())

    # Пагинация
    start = page * cols_per_page
    end = start + cols_per_page
    current_cats = cat_names[start:end]
    
    subtitle = f"Created by: Younqli3ed | Grimoire v0.1 | Page: {page + 1}"
    print("\n" + " " * (tw // 2 - len(subtitle) // 2) + WHITE + subtitle + "\n")

    n = len(current_cats) if current_cats else 1
    total_w = n * w + (n - 1)
    global_pad = " " * max(0, (tw // 2 - total_w // 2))

    if not current_cats:
        print(global_pad + RED + "[!] No more modules on this page.")
    else:
        H, V = "─", "│"
        TL, TR, BL, BR = "┌", "┐", "└", "┘"
        TM, BM, MM = "┬", "┴", "┼"
        ML, MR = "├", "┤"


        print(global_pad + RED + TL + (H*w + TM)*(n-1) + H*w + TR)

        h_line = global_pad + RED + V
        for cat in current_cats:
            h_line += WHITE + Style.BRIGHT + cat.center(w) + RED + V
        print(h_line)
  
        print(global_pad + RED + ML + (H*w + MM)*(n-1) + H*w + MR)


        max_r = max(len(categories[cat]) for cat in current_cats)
        for r in range(max_r):
            line_str = global_pad + RED + V
            for cat in current_cats:
                if r < len(categories[cat]):
                    m = categories[cat][r]
                    txt = f" [{m.id}] {m.name}".ljust(w)
                    line_str += BODY_COLOR + txt + RED + V
                else:
                    line_str += " ".ljust(w) + RED + V
            print(line_str)


        print(global_pad + RED + BL + (H*w + BM)*(n-1) + H*w + BR)
        

        nav_line = f"{RED}[b] back".ljust(total_w - 7) + f"{RED}[n] next page"
        print(global_pad + nav_line + "\n")

    print(f"{global_pad}{RED}Grimoire{WHITE} > ", end="")
    return len(cat_names) # Возвращаем кол-во категорий для логики

if __name__ == "__main__":
    current_page = 0
    cols_per_page = 3
    
    while True:
        all_mods = load_modules()
        total_cats = render_interface(all_mods, page=current_page)
        
        try:
            cmd = input().strip().lower()
        except KeyboardInterrupt:
            break

        if cmd == 'n':
            if (current_page + 1) * cols_per_page < total_cats:
                current_page += 1
            continue
        elif cmd == 'b':
            if current_page > 0:
                current_page -= 1
            continue
        elif cmd in ['exit', 'quit']:
            break
        
        target = next((m for m in all_mods if str(m.id) == cmd), None)
        if target:
            print(f"\n{RED}[*] Starting {target.name}...\n")
            try:
                target.run()
            except Exception as e:
                print(f"{RED}[!] Error: {e}")
            input(f"\n{RED}[!] Press Enter to return...")
