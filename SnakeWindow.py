"""
===============================================================================
                                SNAKE GAME
===============================================================================

Author: Nicolas D'Souza
Date: 2025
Version: 2.0

Description:
Pixel-based Snake game using Python and Tkinter.
Each snake segment is a separate window for smooth movement.
Features:
    - Snake growth and movement
    - Fruit spawning and collision detection
    - Score tracking
    - Game reset on death

Controls:
    - W / Up Arrow    : Move up
    - S / Down Arrow  : Move down
    - A / Left Arrow  : Move left
    - D / Right Arrow : Move right
    - Q               : Quit game
    - R               : Restart game

Notes:
    - Designed for macOS.
    - Time.sleep() controls game speed.
    - Key handling prevents system beeps on invalid keys.

===============================================================================
"""


from tkinter import Tk, Toplevel, Label
import time, random

# Initialize main window
root = Tk()
root.title("Snake Game")

# Grid configuration
PIXEL_SIZE = 25
PIXEL = PIXEL_SIZE

root.update_idletasks()

SCREEN_WIDTH = root.winfo_screenwidth()
SCREEN_HEIGHT = root.winfo_screenheight()

TOP_MARGIN = 50   # menu bar height
BOTTOM_MARGIN = 80  # dock height

USABLE_WIDTH = SCREEN_WIDTH
USABLE_HEIGHT = SCREEN_HEIGHT - (TOP_MARGIN + BOTTOM_MARGIN)

GRID_WIDTH = USABLE_WIDTH - (USABLE_WIDTH % PIXEL_SIZE)
GRID_HEIGHT = USABLE_HEIGHT - (USABLE_HEIGHT % PIXEL_SIZE)

GRID_WIDTH_START = (SCREEN_WIDTH - GRID_WIDTH) // 2
GRID_HEIGHT_START = TOP_MARGIN + (USABLE_HEIGHT - GRID_HEIGHT) // 2

# Game state
is_running = True
game_active = True

# Colors
COLOR_YELLOW = "Yellow"
COLOR_RED = "Red"
COLOR_GREEN = "Green"

"""=== Snake Class ==="""

class Snake:

    def __init__(self):

        # Movement and length properties
        self.step = PIXEL
        self.direction = -1
        self.snake_length = 6
        self.x_pos, self.y_pos = GRID_WIDTH_START, GRID_HEIGHT_START
        self.segments = [[self.x_pos, self.y_pos + i*PIXEL] for i in range(self.snake_length)]
        self.segments.append([None, None])

        # Create windows for each snake segment
        self.windows = []
        self.color = COLOR_GREEN
        self.size = PIXEL
        
        for i in range(self.snake_length):
            self.windows.append(Toplevel(root))
            self.windows[i].configure(bg=self.color)
            self.windows[i].overrideredirect(True)
            self.windows[i].geometry(f"{self.size}x{self.size}+{self.segments[i][0]}+{self.segments[i][1]}")

    def update_position(self):
        """Move the snake forward one step and update segment windows."""

        if self.direction == 1:
            self.y_pos -= self.step
        elif self.direction == -1:
            self.y_pos += self.step
        elif self.direction == -2:
            self.x_pos -= self.step
        elif self.direction == 2:
            self.x_pos += self.step

        for i in range(len(self.segments)-1, -1, -1):
            self.segments[i] = self.segments[i-1]
            self.segments[i-1] = self.segments[i]
        self.segments[0] = (self.x_pos, self.y_pos)

        for i in range(len(self.segments)-1):
            self.windows[i].configure(bg=self.color)
            self.windows[i].geometry(f"{self.size}x{self.size}+{self.segments[i][0]}+{self.segments[i][1]}")

    def handle_key(self, event):
        """Handle user input for movement, quitting, and restarting."""
        global game_active, is_running

        if event.keysym in ["w", "Up"] and self.direction != -1:
            self.direction = 1
        elif event.keysym in ["s", "Down"] and self.direction != 1:
            self.direction = -1
        elif event.keysym in ["a", "Left"] and self.direction != 2:
            self.direction = -2
        elif event.keysym in ["d", "Right"] and self.direction != -2:
            self.direction = 2

        if event.keysym == "q":
            game_active = False
        if event.keysym == "r":
            is_running = False

    def check_wall_collision(self):
        """Stop the game if the snake hits a wall."""
        global is_running
        if (self.x_pos < GRID_WIDTH_START or self.x_pos + self.size > GRID_WIDTH + GRID_WIDTH_START or
            self.y_pos < GRID_HEIGHT_START or self.y_pos + self.size > GRID_HEIGHT + GRID_HEIGHT_START):
            is_running = False

    def check_border_proximity(self):
        """Change color if snake is near the screen border."""
        if (self.x_pos <= GRID_WIDTH_START+PIXEL*5 or self.x_pos + self.size >= (GRID_WIDTH + GRID_WIDTH_START) - PIXEL*5 or
            self.y_pos <= GRID_HEIGHT_START + PIXEL*5 or self.y_pos + self.size >= (GRID_HEIGHT + GRID_HEIGHT_START) - PIXEL*5):
            self.color = COLOR_YELLOW
        else:
            self.color = COLOR_GREEN

    def check_fruit_collision(self):
        """Handle collision with fruit and grow snake."""
        global is_running, points, fruit

        if self.x_pos == fruit.x_pos and self.y_pos == fruit.y_pos:
            fruit.master.destroy()
            fruit = Fruit()
            points.add()
            self.snake_length += 1
            self.segments.append((None, None))
            self.windows.append(Toplevel(root))
            self.windows[-1].configure(bg=self.color)
            self.windows[-1].overrideredirect(True)
            self.windows[-1].geometry(f"{self.size}x{self.size}+{self.segments[-2][0]}+{self.segments[-2][1]}")
            return True
        return False

    def check_self_collision(self):
        """Stop the game if snake collides with itself."""
        global is_running
        for i in range(1, self.snake_length):
            if (self.x_pos, self.y_pos) == self.segments[i]:
                is_running = False

"""=== Fruit Class ==="""

class Fruit:

    def __init__(self):
        self.master = Toplevel(root)
        self.master.overrideredirect(True)
        self.master.config(bg=COLOR_RED)

        self.size = PIXEL
        self.x_pos = (random.randint(0, GRID_WIDTH // PIXEL - 1) * PIXEL + GRID_WIDTH_START)
        self.y_pos = (random.randint(0, GRID_HEIGHT // PIXEL - 1) * PIXEL + GRID_HEIGHT_START)

        self.master.geometry(f"{self.size}x{self.size}+{self.x_pos}+{self.y_pos}")

"""=== Points Class ==="""

class Points:

    def __init__(self):
        self.master = root
        self.master.title("Snake Score")
        self.score = 0

        self.label = Label(self.master, text=f"{self.score}", font=("Arial", 100))
        self.label.pack()

        self.width = 150
        self.height = 100
        self.x_pos = (GRID_WIDTH + GRID_WIDTH_START) - self.width
        self.y_pos = 0
        self.master.geometry(f"{self.width}x{self.height}+{self.x_pos}+{self.y_pos}")

    def add(self):
        """Increment score by one."""
        self.score += 1
        self.label.config(text=f"{self.score}")
        self.label.pack()

    def reset(self):
        """Reset score to zero."""
        self.score = 0
        self.label.config(text=f"{self.score}")
        self.label.pack()

# Game loop functions

def perform_snake_actions():
    
    """Execute all snake actions for each frame."""
    # Make the snake on top of everything

    for i in range(len(snake.masters)):

        snake.masters[i].focus_force()
    snake.update_position()
    snake.check_fruit_collision()
    snake.check_self_collision()
    snake.check_border_proximity()
    snake.check_wall_collision()

# Initialize objects
snake = Snake()
fruit = Fruit()
points = Points()

root.bind_all("<Key>", snake.handle_key)

# Main game loop
while game_active:

    perform_snake_actions()

    if not is_running:
        fruit.master.destroy()
        points.reset()
        for window in snake.windows:
            window.destroy()

        snake = Snake()
        fruit = Fruit()
        root.bind_all("<Key>", snake.handle_key)
        is_running = True

    root.update()
    time.sleep(0.1)
