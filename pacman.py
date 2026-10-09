#!/usr/bin/env python3
import curses
import random
import time 
H,W = 15,21
tick = 0.12
dirs = {"U":(-1,0),"D":(1,0),"L":(0,-1),"R":(0,1)}
OPP = {"U":"D","D":"U","L":"R","R":"L"}

def makemaze():
    g = [["#"]*W for _ in range(H)]
    g[1][1]= " "
    stack=[(1,1)]
    while stack:
        r,c = stack[-1]
        nb = [(r + dr, c+ dc) for dr,dc in ((-2,0), (2,0), (0,-2), (0,2))
            if 1 <= r + dr <= H-2 and 1 <= c + dc <= 9 and g[r+dr][c+dc] == "#"]
        if nb:
            nr,nc = random.choice(nb)
            g[(r+nr)//2][(c+nc)//2] = " "
            g[nr][nc] = " "
            stack.append((nr,nc))
        else:
            stack.pop()
    for r in random.sample(range(1,H-1,2),3):
        g[r][10] = " "
    for r in range(H):
        for c in range(11,W):
            g[r][c] = g[r][W-1-c]
    def openn(r,c):
        return [(r+dr,c+dc) for dr,dc in dirs.values() if g[r+dr][c+dc] == " "]

    for _ in range(300):
        dead = [(r,c) for r in range(1,H-1) for c in range(1,W-1) if g[r][c] == " " and len(openn(r,c)) <= 1]
        if not dead:
            break
        r,c = random.choice(dead)
        wall = [(r+dr,c+dc) for dr,dc in dirs.values()
        if 1<= r + dr < H-1 and 1 <= c + dc < W-1 and g[r+dr][c+dc] == "#"
        and len(openn(r+dr,c+dc)) >= 2]
        if wall:
            wr, wc = random.choice(wall)
            g[wr][wc] = " "
    for r in range(1,H-1):
        for c in range(1,W-1):
            if g[r][c] == "#" and random.random() < 0.10:
                if (g[r - 1][c] == " " and g[r + 1][c] == " ") != (g[r][c - 1] == " " and g[r][c + 1] == " "):
                    g[r][c] = " "
    floor = [(r, c) for r in range(H) for c in range(W) if g[r][c] == " "]
    def nearest(pt, exclude=()):
        return min((p for p in floor if p not in exclude),
                   key=lambda p: (p[0] - pt[0]) ** 2 + (p[1] - pt[1]) ** 2)
    pac=nearest((H-2,10))
    spawn = nearest((H // 2-1, 10), (pac,))
    taken = {pac, spawn}
    for r, c in floor:
        g[r][c] = "."
    for corner in ((1, 1), (1, W - 2), (H - 2, 1), (H - 2, W - 2)):
        p = nearest(corner, taken)
        taken.add(p)
        g[p[0]][p[1]] = "o"
    g[pac[0]][pac[1]] = " "
    g[spawn[0]][spawn[1]] = " "
    return g, pac, spawn


class Game:
    def __init__(self):
        self.hi = 0
        self.new_game()
    def new_game(self):
        self.score, self.lives, self.level = 0, 5, 1
        self.state = "play"
        self.load_level()

    def load_level(self):
        self.grid, self.pac_start, self.spawn = makemaze()
        self.dots = sum(row.count(".") + row.count("o") for row in self.grid)
        self.tick_n = 0
        self.reset_positions()

    def reset_positions(self):
        self.pr, self.pc = self.pac_start
        self.ppr, self.ppc = self.pr, self.pc
        self.pd = self.nd = "L"
        self.fright = 0
        self.ghosts = [dict(r=self.spawn[0], c=self.spawn[1], pr=self.spawn[0], pc=self.spawn[1],
                            d="U", delay=i * 20, afraid=False) for i in range(3)]
    def walk(self, r, c):
        return 0 <= r < H and 0 <= c < W and self.grid[r][c] != "#"
    def handle(self, k):
        m = {curses.KEY_UP: "U", ord("w"): "U", ord("W"): "U",
             curses.KEY_DOWN: "D", ord("s"): "D", ord("S"): "D",
             curses.KEY_LEFT: "L", ord("a"): "L", ord("A"): "L",
             curses.KEY_RIGHT: "R", ord("d"): "R", ord("D"): "R"}
        if k in m:
            self.nd = m[k]
        elif k in (ord("p"), ord("P")) and self.state in ("play", "paused"):
            self.state = "paused" if self.state == "play" else "play"
        elif k in (ord("r"), ord("R")) and self.state == "over":
            self.new_game()
    def move_ghost(self, g):
        opts = [d for d, (dr, dc) in dirs.items() if self.walk(g["r"] + dr, g["c"] + dc)]
        fwd = [d for d in opts if d != OPP[g["d"]]]
        opts = fwd or opts
        if g["afraid"] or random.random() < 0.2:
            d = random.choice(opts)
        else:
            d = min(opts, key=lambda d: (g["r"] + dirs[d][0] - self.pr) ** 2 + (g["c"] + dirs[d][1] - self.pc) ** 2)
        g["d"] = d
        g["r"] += dirs[d][0]
        g["c"] += dirs[d][1]

    def update(self):
        if self.state != "play":
            return
        self.tick_n += 1
        self.ppr, self.ppc = self.pr, self.pc
        dr, dc = dirs[self.nd]
        if self.walk(self.pr + dr, self.pc + dc):
            self.pd = self.nd
        dr, dc = dirs[self.pd]
        if self.walk(self.pr + dr, self.pc + dc):
            self.pr += dr
            self.pc += dc
        cell = self.grid[self.pr][self.pc]
        if cell in ".o":
            self.score += 10 if cell == "." else 50
            self.dots -= 1
            self.grid[self.pr][self.pc] = " "
            if cell == "o":
                self.fright = 60
                for g in self.ghosts:
                    g["afraid"] = True
                    g["d"] = OPP[g["d"]]
        for g in self.ghosts:
            g["pr"], g["pc"] = g["r"], g["c"]
            if g["delay"] > 0:
                g["delay"] -= 1
                continue
            if(g["afraid"] and self.tick_n % 2) or self.tick_n % 5 == 0:
                continue
            self.move_ghost(g)
        for g in self.ghosts:
            same = (g["r"] == self.pr and g["c"] == self.pc)
            swap = (g["r"], g["c"]) == (self.ppr, self.ppc) and (g["pr"], g["pc"]) == (self.pr, self.pc)
            if same or swap:
                if g["afraid"]:
                    self.score += 200
                    g.update(r=self.spawn[0], c=self.spawn[1], pr=self.spawn[0], pc=self.spawn[1],
                             afraid=False, delay=25)
                    for o in self.ghosts:
                        o["afraid"] = False
                    self.fright = 0
                else:
                    self.lives -= 1
                    self.state = "dead" if self.lives > 0 else "over"
                    break
        self.hi = max(self.hi, self.score)
        if self.dots == 0 and self.state == "play":
            self.state="win"
    def draw(self, scr):
        scr.erase()
        hh, ww = scr.getmaxyx()
        if hh < H + 3 or ww < W*2 +2 :
            put(scr, 0, 0, "Window too small",0)
            return scr.refresh()
        put(scr, 0, 0, f"SCORE {self.score}  HI {self.hi}  LIVES {self.lives}  LEVEL {self.level}", curses.A_BOLD)
        ghosts = {(g["r"], g["c"]): g for g in self.ghosts}
        for r in range(H):
            for c in range(W):
                y, x, ch = r + 2, c * 2, self.grid[r][c]
                if (r, c) == (self.pr, self.pc):
                    put(scr, y, x, "C " if self.tick_n % 2 else "O ", curses.color_pair(2) | curses.A_BOLD)
                elif (r, c) in ghosts:
                    if ghosts[(r, c)]["afraid"]:
                        flash = self.fright < 20 and self.tick_n % 2
                        put(scr, y, x, "g ", curses.color_pair(4 if flash else 3) | curses.A_BOLD)
                    else:
                        put(scr, y, x, "G ", curses.color_pair(5) | curses.A_BOLD)
                elif ch == "#":
                    put(scr, y, x, "  ", curses.color_pair(1) | curses.A_REVERSE)
                elif ch == ".":
                    put(scr, y, x, ". ", 0)
                elif ch == "o":
                    put(scr, y, x, "O ", curses.A_BOLD)
        msg = {"paused": "PAUSED - P to resume", "over": "GAME OVER - R restart, Q quit",
               "win": "LEVEL CLEARED!"}.get(self.state)
        if msg:
            put(scr, H + 2, 0, msg, curses.A_BOLD)
        scr.refresh()

def put(scr, y, x, s, attr):
    try:
        scr.addstr(y, x, s, attr)
    except curses.error:
        pass
def run(scr):
    curses.curs_set(0)
    scr.keypad(True)
    scr.timeout(10)
    if curses.has_colors():
        curses.use_default_colors()
        for i, col in enumerate([curses.COLOR_BLUE, curses.COLOR_YELLOW, curses.COLOR_CYAN,
                                 curses.COLOR_WHITE, curses.COLOR_RED], 1):
            curses.init_pair(i, col, -1)
    game = Game()
    last = time.monotonic()
    while True:
        k = scr.getch()
        if k in (ord("q"), ord("Q")):
            return
        game.handle(k)
        if time.monotonic() - last >= tick:
            last = time.monotonic()
            game.update()
            game.draw(scr)
            if game.state == "dead":
                time.sleep(1)
                game.reset_positions()
                game.state = "play"
                curses.flushinp()
            if game.state == "win":
                time.sleep(1.2)
                game.level += 1
                game.load_level()
                curses.flushinp()
                game.state = "play"
if __name__ == "__main__":
    curses.wrapper(run)