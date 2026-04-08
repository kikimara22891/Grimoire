import numpy as np
import os
from colorama import Fore, Style, init

init(autoreset=True)

def get_red_gradient(text):
    length = len(text)
    reds = np.linspace(255, 50, length).astype(int)
    
    gradient_text = ""
    for i, char in enumerate(text):
        r = reds[i]
        gradient_text += f"\033[38;2;{r};0;0m{char}"
    return gradient_text + Style.RESET_ALL

def print_centered(text, gradient=False):
    terminal_width = os.get_terminal_size().columns
    lines = text.split('\n')
    for line in lines:
        centered_line = line.center(terminal_width)
        if gradient:
            print(get_red_gradient(centered_line))
        else:
            print(centered_line)
