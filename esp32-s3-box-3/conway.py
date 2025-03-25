import random
import sdl3
import time

# Window and grid configuration
WIDTH = 320         # Adjusted for a typical MicroPython screen
HEIGHT = 240
CELL_SIZE = 10
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

def init_grid():
    """Initialize the grid with random live (age>=1) or dead (0) cells."""
    return [[random.choice([0, 1]) for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def update_grid(grid):
    """Compute the next generation using Conway's rules with age tracking.
    
    A live cell (grid[y][x] > 0) survives with 2 or 3 live neighbors and ages.
    A dead cell (0) becomes alive with exactly 3 live neighbors.
    """
    new_grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            live_neighbors = 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == 0 and dx == 0:
                        continue
                    ny = (y + dy) % GRID_HEIGHT
                    nx = (x + dx) % GRID_WIDTH
                    if grid[ny][nx] > 0:
                        live_neighbors += 1
            if grid[y][x] > 0:  # Cell is alive.
                if live_neighbors in (2, 3):
                    new_grid[y][x] = grid[y][x] + 1  # Survives and ages.
                else:
                    new_grid[y][x] = 0  # Dies.
            else:
                if live_neighbors == 3:
                    new_grid[y][x] = 1  # New cell born.
                else:
                    new_grid[y][x] = 0
    return new_grid

def get_fill_color(age):
    """Return an (r, g, b) tuple based on cell age.
    
    This function linearly interpolates from dark blue (0, 0, 128)
    for a new cell (age=1) to white (255, 255, 255) for older cells.
    """
    max_age = 10.0
    fraction = age / max_age
    if fraction > 1:
        fraction = 1.0
    # Dark blue: (0, 0, 128); White: (255, 255, 255)
    r = int(0 + fraction * 255)
    g = int(0 + fraction * 255)
    b = int(128 + fraction * (255 - 128))
    return r, g, b

def main():
    # Initialize SDL3 video subsystem.
    if not sdl3.SDL_Init(sdl3.SDL_INIT_VIDEO):
        print("SDL_Init failed")
        return

    # Create an SDL window.
    window = sdl3.SDL_CreateWindow(b"Conway's Game of Life", WIDTH, HEIGHT)
    if not window:
        print("SDL_CreateWindow failed")
        sdl3.SDL_Quit()
        return

    # Create a renderer.
    renderer = sdl3.SDL_CreateRenderer(window, None)
    if not renderer:
        print("SDL_CreateRenderer failed")
        sdl3.SDL_DestroyWindow(window)
        sdl3.SDL_Quit()
        return

    grid = init_grid()
    iterations = 0

    # Main loop.
    while True:
        # Poll events (using our bridging function).
        sdl3.SDL_Update()

        # Update grid.
        grid = update_grid(grid)
        iterations += 1
        if iterations >= 500:
            grid = init_grid()
            iterations = 0

        # Clear screen (black background).
        sdl3.SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255)
        sdl3.SDL_RenderClear(renderer)

        # Draw each live cell.
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                age = grid[y][x]
                if age > 0:
                    #rect = sdl3.SDL_FRect()
                    rect_x = x * CELL_SIZE
                    rect_y = y * CELL_SIZE
                    rect_w = CELL_SIZE
                    rect_h = CELL_SIZE
                    fill_color = get_fill_color(age)
                    sdl3.SDL_SetRenderDrawColor(renderer, fill_color[0], fill_color[1], fill_color[2], 255)
                    sdl3.SDL_RenderDrawRect(renderer, rect_x, rect_y, rect_w, rect_h)
                    # Optionally, draw a 1px white border:
                    # sdl3.SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255)
                    # sdl3.SDL_RenderDrawRect(renderer, rect)
        sdl3.SDL_RenderPresent(renderer)
        time.sleep_ms(50)

    # Cleanup (not reached in this endless loop).
    #sdl3.SDL_DestroyRenderer(renderer)
    #sdl3.SDL_DestroyWindow(window)
    #sdl3.SDL_Quit()

main()


