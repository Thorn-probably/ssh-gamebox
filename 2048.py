import curses
import math
import random
from pacman import put

N = 4
cw,ch, gap = 7, 3, 1
bw = N * cw + (N + 1) * gap
bh = N * ch + (N + 1) * gap
total_h = bh + 5
keys = {curses.KEY_UP: "U", ord("w"): "U", ord("W"): "U",
        curses.KEY_DOWN: "D", ord("s"): "D", ord("S"): "D",
        curses.KEY_LEFT: "L", ord("a"): "L", ord("A"): "L",
        curses.KEY_RIGHT: "R", ord("d"): "R", ord("D"): "R"}

def slide_row(row):
    tiles = [x for x in row if x]
    out, gain, i = [], 0, 0
    while i < len(tiles):
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            out.append(tiles[i] * 2)
            gain += tiles[i] * 2
            i += 2
        else:
            out.append(tiles[i])
            i += 1
    return out + [0] * (N - len(out)), gain

def move(grid, d):
    g = [list(r) for r in grid]
    if d in "UD":
        g = [list(r) for r in zip(*g)]
    if d in "RD":
        g = [r[::-1] for r in g]
    new, gain = [], 0
    for r in g:
        nr , s = slide_row(r)
        new.append(nr)
        gain += s
    if d in "RD":
        new = [r[::-1] for r in new]
    if d in "UD":
        new = [list(r) for r in zip(*new)]
    return new, gain
class Gaem:
    def __init__(self):
        self.best = 0
        self.new_game()

    def new_game(self):
        self.grid = [[0] * N for _ in range(N)]
        self.score = 0
        self.state = "play"
        self.keep_going = False
        self.spawn()
        self.spawn()

    def spawn(self):
        empty = [(r, c) for r in range(N) for c in range(N) if self.grid[r][c] == 0]
        if empty:
            r, c = random.choice(empty)
            self.grid[r][c] = 4 if random.random() < 0.1 else 2
    def can_move(self):
        g = self.grid
        for r in range(N):
            for c in range(N):
                if g[r][c] == 0:
                    return True
                if r + 1 < N and g[r][c] == g[r + 1][c]:
                    return True
                if c + 1 < N and g[r][c] == g[r][c + 1]:
                    return True 
        return False
    
    def handle(self, k) :
        if k in (ord("r"), ord("R")):
            self.new_game()
            return
        if self.state == "won":
            if k in (ord("c"), ord("C")):
                self.keep_going = True
                self.state = "play"
            return
        if self.state == "over":
            return
        d = keys.get(k)
        if not d:
            return
        new, gain = move(self.grid, d)
        if new == self.grid:
            return
        self.grid = new
        self.score += gain
        self.best = max(self.best, self.score)
        self.spawn()
        if not self.keep_going and any (v >= 2048 for r in new for v in r):
            self.state = "won"
        elif not self.can_move():
            self.state = "over"
    def draw(self, scr, pal):
        scr.erase()
        hh, ww = scr.getmaxyx()
        if hh < total_h or ww < bw:
            put(scr, 0, 0, "Window too small", 0)
            return scr.refresh()
        oy, ox = (hh- total_h)//2, (ww-bw)//2
        put (scr, oy, ox, f"2028    SCORE {self.score}  BEST {self.best}", curses.A_BOLD)
        by = oy + 2
        for y in range(bh):
            put(scr, by + y, ox, " " * bw, pal.frame)
        for r in range(N):
            for c in range(N):
                v = self.grid[r][c]
                y, x = by + gap + r * (ch + gap), ox + gap + c * (cw + gap)
                attr = pal.tile(v)
                if v:
                    put(scr, y + ch // 2, x, str(v).center(cw), attr | curses.A_BOLD)
        msg = {"won": "YOU MADE 2048! - C to continue, R to restart",
               "over": "GAME OVER - R to restart"}.get(self.state, "arrows/WASD to move, R to restart, Q to quit")
        put(scr, by + bh + 1, ox + max(0, (bw - len(msg)) // 2), msg, curses.A_BOLD if self.state != "play" else 0)
        scr.refresh()

class pallete:
    def __init__(self):
        self.has = curses.has_colors()
        self.frame = curses.A_REVERSE
        self.empty = 0
        self.levels = []
        if not self.has:
            return
        if curses.COLORS >= 256:      # 256-colour terminal (xterm-256color etc.)
            bgs = [252, 223, 216, 209, 203, 196, 229, 227, 220, 214, 208, 171]
            white_text = {3, 4, 5, 10, 11}
            for i, bg in enumerate(bgs):
                curses.init_pair(1 + i, 231 if i in white_text else 16, bg)
                self.levels.append(curses.color_pair(1 + i))
            curses.init_pair(30, 231, 238)
            curses.init_pair(31, 231, 236)
            self.frame, self.empty = curses.color_pair(30), curses.color_pair(31)
        else:
            B, W_ = curses.COLOR_BLACK, curses.COLOR_WHITE
            combo = [(B, W_), (B, curses.COLOR_CYAN), (B, curses.COLOR_GREEN),
                     (B, curses.COLOR_YELLOW), (W_, curses.COLOR_RED), (W_, curses.COLOR_MAGENTA)]
            for i, (fg, bg) in enumerate(combo):
                curses.init_pair(1 + i, fg, bg)
                self.levels.append(curses.color_pair(1 + i))
            curses.init_pair(30, W_, curses.COLOR_BLUE)
            self.frame = curses.color_pair(30)
    def tile(self, v):
        if v == 0:
            return self.empty
        if not self.has:
            return curses.A_BOLD
        i = int(math.log2(v)) - 1
        if i < len(self.levels):
            return self.levels[i]
        return self.levels[i % len(self.levels)] | curses.A_BOLD
def run(scr):
    curses.curs_set(0)
    scr.keypad(True)
    scr.timeout(-1)
    pal = pallete()
    g = Gaem()
    while True:
        g.draw(scr, pal)
        k = scr.getch()
        if k in (ord("q"), ord("Q")):
            break
        g.handle(k)

if __name__ == "__main__":
    curses.wrapper(run)