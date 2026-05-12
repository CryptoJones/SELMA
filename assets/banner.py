#!/usr/bin/env python3
"""SELMA — ANSI color banner + American flag. Run: python3 assets/banner.py"""

R  = "\033[91m"    # bright red
W  = "\033[97m"    # bright white
B  = "\033[94m"    # bright blue
YL = "\033[93m"    # yellow/gold
X  = "\033[0m"     # reset

# Background colors for the flag
BG_RED  = "\033[41m"
BG_WHT  = "\033[107m"
BG_BLU  = "\033[44m"
FG_WHT  = "\033[97m"   # white text (for stars on blue)

# Big block letters for S E L M A
S = [" ███ ", "█    ", " ██  ", "   █ ", "███  "]
E = ["████ ", "█    ", "███  ", "█    ", "████ "]
L = ["█    ", "█    ", "█    ", "█    ", "████ "]
M = ["█   █", "██ ██", "█ █ █", "█   █", "█   █"]
A = [" ███ ", "█   █", "█████", "█   █", "█   █"]

letters       = [S, E, L, M, A]
letter_colors = [R, W, B, R, W]


def american_flag():
    flag_w   = 67   # total flag width in chars
    canton_w = 24   # blue canton width
    stripe_w = flag_w - canton_w

    def star_row(six):
        """Return a canton-width string with 6 or 5 evenly-spaced stars."""
        row = [" "] * canton_w
        if six:
            positions = [0, 4, 8, 12, 16, 20]   # 6 stars
        else:
            positions = [2, 6, 10, 14, 18]       # 5 stars
        for p in positions:
            row[p] = "*"
        return "".join(row)

    indent = "    "
    for i in range(13):
        bg = BG_RED if i % 2 == 0 else BG_WHT
        if i < 7:
            stars = star_row(i % 2 == 0)
            print(f"{indent}{BG_BLU}{FG_WHT}{stars}{X}{bg}{' ' * stripe_w}{X}")
        else:
            print(f"{indent}{bg}{' ' * flag_w}{X}")

    print()


def banner():
    width = 63

    stars_row = f"  {YL}★{X}   {YL}★{X}   {YL}★{X}   {YL}★{X}   {YL}★{X}   {YL}★{X}   {YL}★{X}   {YL}★{X}   {YL}★{X}  "

    print()
    american_flag()
    print(f"     {stars_row}")
    print(f"  {B}╔{'═' * width}╗{X}")
    print(f"  {B}║{' ' * width}║{X}")
    print(f"  {B}║  {R}╔{'═' * (width - 6)}╗{X}  {B}║{X}")
    print(f"  {B}║  {R}║{X}  {YL}⚖{X}  {W}LAW ENFORCEMENT STATUTORY ANALYSIS{X}  {YL}⚖{X}  {R}║{X}  {B}║{X}")
    print(f"  {B}║  {R}║{' ' * (width - 6)}║{X}  {B}║{X}")

    for row in range(5):
        combined = "  "
        for i, (letter, color) in enumerate(zip(letters, letter_colors)):
            combined += f"{color}{letter[row]}{X}"
            if i < len(letters) - 1:
                combined += " "
        combined += "  "

        raw_len = sum(len(l[row]) for l in letters) + len(letters) - 1 + 4
        pad = width - 6 - raw_len
        lp = pad // 2
        rp = pad - lp
        print(f"  {B}║  {R}║{X}{' ' * lp}{combined}{' ' * rp}{R}║{X}  {B}║{X}")

    print(f"  {B}║  {R}║{' ' * (width - 6)}║{X}  {B}║{X}")

    subtitle = "Specified Encapsulated Limitless Memory Archive"
    pad = width - 6 - len(subtitle)
    lp, rp = pad // 2, pad - pad // 2
    print(f"  {B}║  {R}║{X}{' ' * lp}{W}{subtitle}{X}{' ' * rp}{R}║{X}  {B}║{X}")

    print(f"  {B}║  {R}║{' ' * (width - 6)}║{X}  {B}║{X}")

    registry = "ollama run Ronin48/selma"
    pad = width - 6 - len(registry)
    lp, rp = pad // 2, pad - pad // 2
    print(f"  {B}║  {R}║{X}{' ' * lp}{B}{registry}{X}{' ' * rp}{R}║{X}  {B}║{X}")

    print(f"  {B}║  {R}╚{'═' * (width - 6)}╝{X}  {B}║{X}")
    print(f"  {B}║{' ' * width}║{X}")
    print(f"  {B}╚{'═' * width}╝{X}")
    print(f"     {stars_row}")
    print()


if __name__ == "__main__":
    banner()
