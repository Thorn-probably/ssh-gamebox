#!/usr/bin/env python3
import curses
import os
import random
import sys
import snake
import pacman

banner = [
    r"  ____    _    __  __ _____ ____   _____  __ ",
    r" / ___|  / \  |  \/  | ____| __ ) / _ \ \/ / ",
    r"| |  _  / _ \ | |\/| |  _| |  _ \| | | \  /  ",
    r"| |_| |/ ___ \| |  | | |___| |_) | |_| /  \  ",
    r" \____/_/   \_\_|  |_|_____|____/ \___/_/\_\ ",
]
GAMES = [
    ("Pacman", pacman.run),
    ("Snake", snake.run)
]

def put(scr, y, x, s, attr=0):
    try:
        scr.addstr(y, x, s, attr)
    except curses.error:
        pass

def draw_menu(scr, selected_idx):
    scr.erase()
    max_y, max_x = scr.getmaxyx()

    # Minimum terminal requirement
    if max_y < 20 or max_x < 55:
        put(scr, 0, 0, "Terminal window too small. Resize to at least 55x20.")
        scr.refresh()
        return

    start_y = 2
    banner_width = max(len(line) for line in banner)
    banner_x = max(2, (max_x - banner_width) // 2)
    for i, line in enumerate(banner):
        put(scr, start_y + i, banner_x, line, curses.color_pair(3) | curses.A_BOLD)

    sub = ":: TERMINAL ARCADE SSH EDITION ::"
    put(scr, start_y + len(banner) + 1, max(2, (max_x - len(sub)) // 2), sub, curses.color_pair(4))

    menu_start_y = start_y + len(banner) + 4
    for idx, (name, _) in enumerate(GAMES):
        y = menu_start_y + (idx * 2)
        label = f" [ {idx + 1} ]  {name.upper()} "
        x = max(4, (max_x - len(label)) // 2)

        if idx == selected_idx:
            # Highlight selected row
            put(scr, y, x - 2, "> " + label + " <", curses.color_pair(2) | curses.A_BOLD | curses.A_REVERSE)
        else:
            put(scr, y, x, label, curses.color_pair(4) | curses.A_BOLD)
    hint1 = "[W/S or Up/Down] Select   |   [ENTER / 1 / 2] Play"
    hint2 = "[Q] Exit Gamebox"
    put(scr, max_y - 3, max(2, (max_x - len(hint1)) // 2), hint1, curses.color_pair(1))
    put(scr, max_y - 2, max(2, (max_x - len(hint2)) // 2), hint2, curses.color_pair(5))

    scr.refresh()
def menu_loop(scr):
    curses.curs_set(0)
    scr.keypad(True)
    scr.timeout(50)
    if curses.has_colors():
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_BLUE, -1)
        curses.init_pair(2, curses.COLOR_YELLOW, -1)
        curses.init_pair(3, curses.COLOR_CYAN, -1)
        curses.init_pair(4, curses.COLOR_WHITE, -1)
        curses.init_pair(5, curses.COLOR_RED, -1)

    selected = 0

    while True:
        draw_menu(scr, selected)
        k = scr.getch()

        if k in (ord("q"), ord("Q")):
            break
        elif k in (curses.KEY_UP, ord("w"), ord("W")):
            selected = (selected - 1) % len(GAMES)
        elif k in (curses.KEY_DOWN, ord("s"), ord("S")):
            selected = (selected + 1) % len(GAMES)
        elif k in (ord("1"), ord("2")):
            idx = int(chr(k)) - 1
            if 0 <= idx < len(GAMES):
                launch_game(scr, GAMES[idx][1])
        elif k in (curses.KEY_ENTER, 10, 13, 32):  # Enter or Space
            launch_game(scr, GAMES[selected][1])

def launch_game(scr, runner):
    scr.clear()
    scr.refresh()
    try:
        runner(scr)
    except Exception as e:
        pass
    finally:
        curses.curs_set(0)
        scr.keypad(True)
        scr.timeout(50)
        scr.clear()


def main():
    try:
        curses.wrapper(menu_loop)
    except KeyboardInterrupt:
        pass
    finally:
        os.system("clear")
        print("Thanks for playing! Goodbye.")

if __name__ == "__main__":
    main()