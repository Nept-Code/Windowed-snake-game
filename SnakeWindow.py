"""
===============================================================================
                                SNAKE GAME
===============================================================================

Author: Nicolas D'Souza
Date: 2025
Version: 1.0

Description:
A borderless, pixel-based Snake game using Python and Tkinter.
Each snake segment is represented by a separate window for smooth movement.

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

Notes:
    - Designed for macOS with borderless windows.
    - Time.sleep() controls game speed.
    - Key handling prevents system beeps on invalid keys.

===============================================================================
"""

# Imports
from tkinter import Tk, Toplevel, Label
import time, random

# Initialize main window
root = Tk()
root.title("Snake Game")

# Grid configuration
PIXEL_SIZE = 50
GRID_HEIGHT = int(root.winfo_screenheight() - root.winfo_screenheight() % PIXEL_SIZE)
GRID_HEIGHT_START = int((root.winfo_screenheight() / 2) - (GRID_HEIGHT / 2))
GRID_WIDTH = int(root.winfo_screenwidth() - root.winfo_screenwidth() % PIXEL_SIZE)
GRID_WIDTH_START = int((root.winfo_screenwidth() / 2) - (GRID_WIDTH / 2))
PIXEL = GRID_WIDTH // PIXEL_SIZE

# Game state variables
is_running = True
game_active = True

# Colors
COLOR_YELLOW = "Yellow"
COLOR_RED = "Red"
COLOR_GREEN = "Green"


"""=== Snake Class ==="""

class Snake:
    def __init__(self):
        # Movement and size properties
        self.step_size = PIXEL
        self.direction = -1
        self.length = 6
        self.x_pos, self.y_pos = GRID_WIDTH_START, GRID_HEIGHT_START
        self.positions = [[self.x_pos, self.y_pos + i] for i in range(self.length)]
        self.positions.append([None, None])  # Placeholder for tail growth

        # Create windows for each snake segment
        self.segments = []
        self.color = COLOR_GREEN
        self.size = PIXEL
        
        for i in range(self.length):
            self.segments.append(Toplevel(root))
            self.segments[i].configure(bg=self.color)
            self.segments[i].overrideredirect(True)
            self.segments[i].geometry(f"{self.size}x{self.size}+{self.positions[i][0]}+{self.positions[i][1]}")

    def update_position(self):
        """Move the snake based on current direction and update segment positions."""
        if self.direction == 1:
            self.y_pos -= self.step_size
        elif self.direction == -1:
            self.y_pos += self.step_size
        elif self.direction == -2:
            self.x_pos -= self.step_size
        elif self.direction == 2:
            self.x_pos += self.step_size

        # Update positions list
        for i in range(len(self.positions)-1, -1, -1):
            self.positions[i] = self.positions[i-1]
            self.positions[i-1] = self.positions[i]
        self.positions[0] = (self.x_pos, self.y_pos)

        # Refresh segment windows
        for i in range(len(self.positions)-1):
            self.segments[i].configure(bg=self.color)
            self.segments[i].geometry(f"{self.size}x{self.size}+{self.positions[i][0]}+{self.positions[i][1]}")

    def handle_key(self, event):
        """Handle keypress events for snake movement and quitting."""
        global game_active

        # Movement keys
        if event.keysym in ["w", "Up"] and self.direction != -1:
            self.direction = 1
        elif event.keysym in ["s", "Down"] and self.direction != 1:
            self.direction = -1
        elif event.keysym in ["a", "Left"] and self.direction != 2:
            self.direction = -2
        elif event.keysym in ["d", "Right"] and self.direction != -2:
            self.direction = 2

        # Quit key
        if event.keysym == "q":
            game_active = False

    def check_wall_collision(self):
        """Stop the game if snake goes out of bounds."""
        global is_running
        if (self.x_pos < GRID_WIDTH_START or self.x_pos + self.size > GRID_WIDTH+GRID_WIDTH_START or
            self.y_pos < GRID_HEIGHT_START or self.y_pos + self.size > GRID_HEIGHT+GRID_HEIGHT_START):
            is_running = False

    def update_color_near_border(self):
        """Change snake color when near the edges."""
        if (self.x_pos <= GRID_WIDTH_START+PIXEL*5 or self.x_pos + self.size >= (GRID_WIDTH+GRID_WIDTH_START)-PIXEL*5 or
            self.y_pos <= GRID_HEIGHT_START + PIXEL*5 or self.y_pos + self.size >= (GRID_HEIGHT+GRID_HEIGHT_START)-PIXEL*5):
            self.color = COLOR_YELLOW
        else:
            self.color = COLOR_GREEN

    def check_fruit_collision(self):
        """Check if snake collides with fruit and grow snake."""
        global is_running, points, fruit

        if self.x_pos == fruit.x_pos and self.y_pos == fruit.y_pos:
            # Remove old fruit and spawn new one
            fruit.master.destroy()
            fruit = Fruit()

            # Add a point
            points.add()

            # Grow snake
            self.length += 1
            self.positions.append((None, None))
            self.segments.append(Toplevel(root))
            self.segments[-1].configure(bg=self.color)
            self.segments[-1].overrideredirect(True)
            self.segments[-1].geometry(f"{self.size}x{self.size}+{self.positions[-2][0]}+{self.positions[-2][1]}")

            return True
        return False

    def check_self_collision(self):
        """Stop the game if snake collides with itself."""
        global is_running
        for i in range(1, self.length):
            if (self.x_pos, self.y_pos) == self.positions[i]:
                is_running = False


"""=== Fruit Class ==="""

class Fruit:
    def __init__(self):
        # Fruit window
        self.master = Toplevel(root)
        self.master.overrideredirect(True)
        self.master.config(bg=COLOR_RED)

        # Fruit properties
        self.size = PIXEL
        self.x_pos = (random.randint(0, GRID_WIDTH // PIXEL) * PIXEL + GRID_WIDTH_START)
        self.y_pos = (random.randint(0, GRID_HEIGHT // PIXEL) * PIXEL + GRID_HEIGHT_START)

        # Set window position
        self.master.geometry(f"{self.size}x{self.size}+{self.x_pos}+{self.y_pos}")


"""=== Points Class ==="""

class Points:
    def __init__(self):
        # Score window
        self.master = root
        self.master.title("Snake Score")
        self.points = 0

        # Label configuration
        self.label = Label(self.master, text=f"{self.points}", font=("Arial", 100))
        self.label.pack()

        # Window geometry
        self.width = 150
        self.height = 100
        self.x_pos = (GRID_WIDTH + GRID_WIDTH_START) - self.width
        self.y_pos = 0
        self.master.geometry(f"{self.width}x{self.height}+{self.x_pos}+{self.y_pos}")

    def add(self):
        """Increment score by one."""
        self.points += 1
        self.label.config(text=f"{self.points}")
        self.label.pack()


# Game logic functions
def perform_snake_actions():
    """Perform all snake actions in one frame."""
    snake.update_position()
    snake.check_fruit_collision()
    snake.check_self_collision()
    snake.update_color_near_border()
    snake.check_wall_collision()


# Instantiate game objects
snake = Snake()
fruit = Fruit()
points = Points()

# Bind keyboard events
root.bind_all("<Key>", snake.handle_key)

# Main game loop
while game_active:
    perform_snake_actions()

    # Reset game if snake dies
    if not is_running:
        fruit.master.destroy()
        for i in range(snake.length):
            snake.segments[i].destroy()
        snake = Snake()
        fruit = Fruit()
        points = Points()
        root.bind_all("<Key>", snake.handle_key)
        is_running = True

    # Refresh display and control frame rate
    root.update()
    time.sleep(0.1)
