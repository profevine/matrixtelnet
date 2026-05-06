import random
import time
import os
import shutil

# ANSI escape codes for color and clearing
GREEN = "\033[32m"
BRIGHT_GREEN = "\033[92m"
RESET = "\033[0m"
CLEAR = "\033[H\033[J"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"

CHARACTERS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+-=[]{}|;:,.<>?/\\"

class MatrixRain:
    def __init__(self, width=None, height=None):
        self.width, self.height = shutil.get_terminal_size((80, 24))
        if width: self.width = width
        if height: self.height = height
        
        # Each column has a "lead" character position, a speed, and a length
        self.columns = [0] * self.width
        self.speeds = [random.randint(1, 3) for _ in range(self.width)]
        self.next_update = [0] * self.width
        self.trails = [[] for _ in range(self.width)] # List of (y, char, is_bright)
        
    def update(self):
        for x in range(self.width):
            self.next_update[x] -= 1
            if self.next_update[x] <= 0:
                self.next_update[x] = self.speeds[x]
                
                # Update trail
                new_y = self.columns[x]
                char = random.choice(CHARACTERS)
                self.trails[x].insert(0, [new_y, char, True])
                
                # Move lead down
                self.columns[x] += 1
                
                # If lead off screen, occasionally reset
                if self.columns[x] > self.height + 20:
                    if random.random() > 0.95:
                        self.columns[x] = 0
                        self.trails[x] = []
                
                # Update trail brightness/persistence
                for i in range(len(self.trails[x])):
                    self.trails[x][i][2] = (i == 0) # Only first is bright
                
                # Trim trail
                if len(self.trails[x]) > random.randint(5, 15):
                    self.trails[x].pop()

    def get_frame(self):
        screen = [[" " for _ in range(self.width)] for _ in range(self.height)]
        
        for x in range(self.width):
            for y, char, is_bright in self.trails[x]:
                if 0 <= y < self.height:
                    color = BRIGHT_GREEN if is_bright else GREEN
                    screen[y][x] = f"{color}{char}{RESET}"
        
        return CLEAR + "\n".join("".join(row) for row in screen)

def run_locally():
    rain = MatrixRain()
    print(HIDE_CURSOR, end="")
    try:
        while True:
            rain.update()
            print(rain.get_frame(), end="", flush=True)
            time.sleep(0.05)
    except KeyboardInterrupt:
        print(SHOW_CURSOR)
        print(RESET + SHOW_CURSOR + "\nGoodbye, Neo.")

if __name__ == "__main__":
    run_locally()
