#!/usr/bin/env python3
import curses
import random
import time

H,W = 15,21
tick = 0.10
dirs = {"U":(-1,0),"D":(1,0),"L":(0,-1),"R":(0,1)}
OPP = {"U":"D","D":"U","L":"R","R":"L"}

class SnakeGame:
    def __init__(self):
        self.hi = 0
        self.new_game()

    def new_game(self):
        self.score = 0
        self.state = "play"
        self.tick_n = 0
        self.d = "R"
        self.nd = "R"
        mid_r, mid_c = H // 2, W // 2
        self.body = [(mid_r, mid_c), (mid_r, mid_c - 1), (mid_r, mid_c - 2)]
        self.foods = set()
        self.spawn_foods()
        

    def spawn_foods(self):
        target_food_count = random.randint(1, 3)  # Randomly spawn 1 to 3 food items
        while len(self.foods) < target_food_count:
            empty = [
                (r,c) for r in range(1,H-1) for c in range(1,W-1)
                if (r,c) not in self.body and (r,c) not in self.foods
            ]
            if not empty:
                break  # No more space to spawn food
            self.foods.add(random.choice(empty))




    def handle(self, k):
        m = {
            curses.KEY_UP: "U", ord("w"): "U", ord("W"): "U",
            curses.KEY_DOWN: "D", ord("s"): "D", ord("S"): "D",
            curses.KEY_LEFT: "L", ord("a"): "L", ord("A"): "L",
            curses.KEY_RIGHT: "R", ord("d"): "R", ord("D"): "R",
        }
        if k in m:
            new_d = m[k]
            if new_d != OPP[self.d]:  # Prevent reversing direction
                self.nd = new_d
        elif k in (ord("p"), ord("P")) and self.state in ("play", "paused"):
            self.state = "paused" if self.state == "play" else "play"
        elif k in (ord("r"), ord("R")) and self.state == "over":
            self.new_game()
    def update(self):
        if self.state != "play":
            return
        self.tick_n += 1
        self.d = self.nd
        dr, dc = dirs[self.d]
        head_r, head_c = self.body[0]
        nr, nc = head_r + dr, head_c + dc
        nr = 1 + (head_r + dr - 1) % (H - 2)  # Wrap around vertically
        nc = 1 + (head_c + dc - 1) % (W -2)  # Wrap around horizontally
        # Self collision (exclude tail tip because it moves forward unless eating)
        if (nr, nc) in self.body[:-1]:
            self.state = "over"
            return          
        self.body.insert(0, (nr, nc))  # Move head
        if self.foods and (nr, nc) in self.foods:
            self.score += 10
            self.hi = max(self.hi, self.score)
            self.foods.remove((nr, nc))
            self.spawn_foods()
            if not self.foods:
                self.state = "over"  # No more space for food, game over
        else:
            self.body.pop()  # Don't remove tail, snake grows
    def draw(self, scr):
        scr.erase()
        hh, ww = scr.getmaxyx()
        if hh < H + 3 or ww < W * 2 + 2:
            put(scr, 0, 0, "Window too small", 0)
            return scr.refresh()
        put(scr, 0, 0, f"SCORE {self.score}  HI {self.hi}  LEN {len(self.body)}", curses.A_BOLD)

        body_set = set(self.body)
        head = self.body[0]

        for r in range(H):
            for c in range(W):
                y, x = r + 2, c * 2
                # Outer border
                if r == 0 or r == H - 1 or c == 0 or c == W - 1:
                    put(scr, y, x, "  ", curses.color_pair(1) | curses.A_REVERSE)
                elif (r, c) == head:
                    put(scr, y, x, "@@", curses.color_pair(2) | curses.A_BOLD)
                elif (r, c) in body_set:
                    put(scr, y, x, "[]", curses.color_pair(3) | curses.A_BOLD)
                elif (r, c) in self.foods:
                    put(scr, y, x, "<>", curses.color_pair(5) | curses.A_BOLD)
                else:
                    put(scr, y, x, "  ", 0)  
        msg = {
            "paused": "PAUSED - Press P to resume",
            "over": "GAME OVER - Press R to restart, Q to quit",
        }.get(self.state, "")
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
        for i, col in enumerate(
            [curses.COLOR_BLUE, curses.COLOR_YELLOW, curses.COLOR_GREEN,
             curses.COLOR_WHITE, curses.COLOR_RED], 1
        ):
            curses.init_pair(i, col, -1)

    game = SnakeGame()
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

if __name__ == "__main__":
    curses.wrapper(run)