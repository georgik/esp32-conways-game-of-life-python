import random
import ctypes
import sdl3
import colorsys

# Window and grid configuration
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 10
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

def init_grid():
    """Initialize the grid with random live (age >=1) or dead (0) cells."""
    # For live cells, the age starts at 1.
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
            if grid[y][x] > 0:  # cell is alive
                if live_neighbors in (2, 3):
                    new_grid[y][x] = grid[y][x] + 1  # cell survives and ages
                else:
                    new_grid[y][x] = 0  # cell dies
            else:
                if live_neighbors == 3:
                    new_grid[y][x] = 1  # cell is born with age 1
                else:
                    new_grid[y][x] = 0
    return new_grid

import colorsys

def get_fill_color(age):
    """Return an RGB tuple for the fill color based on the cell's age.
    
    Younger cells are rendered as a lighter, saturated blue, while older cells 
    transition toward white. The saturation decreases and brightness increases 
    with age.
    """
    max_age = 10  # maximum age for color scaling
    fraction = min(age / max_age, 1.0)
    hue = 0.66  # fixed hue for blue
    # For a young cell: high saturation (blue) and a higher base brightness (0.5)
    # For an old cell: saturation drops to 0 and brightness reaches 1 (white)
    saturation = 1.0 - fraction
    value = 0.5 + fraction * (1.0 - 0.5)  # transitions from 0.5 to 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    return int(r * 255), int(g * 255), int(b * 255)


def main():
    # Initialize SDL3 video subsystem
    if not sdl3.SDL_Init(sdl3.SDL_INIT_VIDEO):
        print("SDL could not initialize:", sdl3.SDL_GetError().decode())
        return

    # Create an SDL window
    window = sdl3.SDL_CreateWindow(
        b"Conway's Game of Life",
        WIDTH, HEIGHT,
        sdl3.SDL_WINDOW_RESIZABLE
    )
    if not window:
        print("Window could not be created:", sdl3.SDL_GetError().decode())
        sdl3.SDL_Quit()
        return

    # Create a renderer using accelerated rendering
    renderDrivers = [sdl3.SDL_GetRenderDriver(i).decode() for i in range(sdl3.SDL_GetNumRenderDrivers())]
    tryGetDriver, tryUseVulkan = lambda order, drivers: next((i for i in order if i in drivers), None), False
    renderDriver = tryGetDriver((["vulkan"] if tryUseVulkan else []) + ["opengl", "software"], renderDrivers)
    print(f"available render drivers: {', '.join(renderDrivers)} (current: {renderDriver}).")
    if not (renderer := sdl3.SDL_CreateRenderer(window, renderDriver.encode())):
        print(f"failed to create renderer: {sdl3.SDL_GetError().decode().lower()}.")
        return -1

    grid = init_grid()
    iterations = 0
    running = True
    event = sdl3.SDL_Event()

    # Main loop
    while running:
        # Process events; note that SDL_Event must be passed as a pointer.
        while sdl3.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl3.SDL_EVENT_QUIT:
                running = False

        # Update the grid state and increment iteration count
        grid = update_grid(grid)
        iterations += 1
        if iterations >= 500:
            grid = init_grid()
            iterations = 0

        # Clear the screen (black background)
        sdl3.SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255)
        sdl3.SDL_RenderClear(renderer)

        # Draw each live cell: fill with color based on age and a 1px white border.
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                age = grid[y][x]
                if age > 0:
                    rect = sdl3.SDL_FRect()
                    rect.x = float(x * CELL_SIZE)
                    rect.y = float(y * CELL_SIZE)
                    rect.w = float(CELL_SIZE)
                    rect.h = float(CELL_SIZE)
                    # Fill the cell with a color determined by its age.
                    fill_color = get_fill_color(age)
                    sdl3.SDL_SetRenderDrawColor(renderer, fill_color[0], fill_color[1], fill_color[2], 255)
                    sdl3.SDL_RenderFillRect(renderer, rect)
                    # # Draw a 1px white border using the new SDL_RenderDrawRectF API.
                    # sdl3.SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255)
                    # sdl3.SDL_RenderDrawRectF(renderer, rect)

        # Present the rendered frame
        sdl3.SDL_RenderPresent(renderer)
        sdl3.SDL_Delay(100)  # Delay in milliseconds

    # Cleanup and quit
    sdl3.SDL_DestroyRenderer(renderer)
    sdl3.SDL_DestroyWindow(window)
    sdl3.SDL_Quit()

if __name__ == "__main__":
    main()
