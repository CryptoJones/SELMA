#!/usr/bin/env python3
"""SELMA — ANSI color banner. Run: python3 assets/banner.py"""

R  = "\033[91m"   # bright red
W  = "\033[97m"   # bright white
B  = "\033[94m"   # bright blue
YL = "\033[93m"   # yellow (stars/gold)
X  = "\033[0m"    # reset

# Big block letters for S E L M A
S = [
    " ███ ",
    "█    ",
    " ██  ",
    "   █ ",
    "███  ",
]
E = [
    "████ ",
    "█    ",
    "███  ",
    "█    ",
    "████ ",
]
L = [
    "█    ",
    "█    ",
    "█    ",
    "█    ",
    "████ ",
]
M = [
    "█   █",
    "██ ██",
    "█ █ █",
    "█   █",
    "█   █",
]
A = [
    " ███ ",
    "█   █",
    "█████",
    "█   █",
    "█   █",
]

letters      = [S, E, L, M, A]
letter_colors = [R, W, B, R, W]

def banner():
    width = 63

    def line(color, text, fill=" ", align="center"):
        inner = text.center(width - 4) if align == "center" else f" {text:<{width-5}} "
        return f"{color}║{X}{W}{inner}{X}{color}║{X}"

    # Stars row
    stars = f"  {YL}★{X}   {YL}★{X}   {YL}★{X}   {YL}★{X}   {YL}★{X}   {YL}★{X}   {YL}★{X}   {YL}★{X}   {YL}★{X}  "

    print()
    print(f"     {stars}")
    print(f"  {B}╔{'═' * (width)}╗{X}")
    print(f"  {B}║{' ' * width}║{X}")
    print(f"  {B}║  {R}╔{'═' * (width - 6)}╗{X}  {B}║{X}")

    # Badge inner top
    print(f"  {B}║  {R}║{X}  {YL}⚖{X}  {W}LAW ENFORCEMENT STATUTORY ANALYSIS{X}  {YL}⚖{X}  {R}║{X}  {B}║{X}")
    print(f"  {B}║  {R}║{' ' * (width - 6)}║{X}  {B}║{X}")

    # Big letters — 5 rows tall
    for row in range(5):
        # Build the combined letter row with colors
        combined = "  "
        for i, (letter, color) in enumerate(zip(letters, letter_colors)):
            combined += f"{color}{letter[row]}{X}"
            if i < len(letters) - 1:
                combined += " "
        combined += "  "

        # Pad to fill the inner box width
        raw_len = sum(len(l[row]) for l in letters) + len(letters) - 1 + 4
        pad = width - 6 - raw_len
        left_pad = pad // 2
        right_pad = pad - left_pad

        print(f"  {B}║  {R}║{X}{' ' * left_pad}{combined}{' ' * right_pad}{R}║{X}  {B}║{X}")

    print(f"  {B}║  {R}║{' ' * (width - 6)}║{X}  {B}║{X}")

    # Subtitle
    subtitle = "Specified Encapsulated Limitless Memory Archive"
    pad = width - 6 - len(subtitle)
    lp = pad // 2
    rp = pad - lp
    print(f"  {B}║  {R}║{X}{' ' * lp}{W}{subtitle}{X}{' ' * rp}{R}║{X}  {B}║{X}")

    print(f"  {B}║  {R}║{' ' * (width - 6)}║{X}  {B}║{X}")

    # Website / registry
    registry = "ollama run Ronin48/selma"
    pad = width - 6 - len(registry)
    lp = pad // 2
    rp = pad - lp
    print(f"  {B}║  {R}║{X}{' ' * lp}{B}{registry}{X}{' ' * rp}{R}║{X}  {B}║{X}")

    print(f"  {B}║  {R}╚{'═' * (width - 6)}╝{X}  {B}║{X}")
    print(f"  {B}║{' ' * width}║{X}")
    print(f"  {B}╚{'═' * width}╝{X}")
    print(f"     {stars}")
    print()

if __name__ == "__main__":
    banner()
