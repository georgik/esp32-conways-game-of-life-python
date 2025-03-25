import random
import ctypes
import sdl3

# Window and grid configuration
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 10
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

def init_grid():
    """Initialize the grid with random live (1) or dead (0) cells."""
    return [[random.choice([0, 1]) for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def update_grid(grid):
    """Compute the next generation of the grid using Conway's rules."""
    new_grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            # Count live neighbors with wrap-around at edges
            neighbors = 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == 0 and dx == 0:
                        continue
                    ny = (y + dy) % GRID_HEIGHT
                    nx = (x + dx) % GRID_WIDTH
                    neighbors += grid[ny][nx]
            # Apply Conway's rules
            if grid[y][x] == 1:
                new_grid[y][x] = 1 if 2 <= neighbors <= 3 else 0
            else:
                new_grid[y][x] = 1 if neighbors == 3 else 0
    return new_grid

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
    running = True
    event = sdl3.SDL_Event()

    # Main loop
    while running:
        # Process events; note that SDL_Event must be passed as a pointer.
        while sdl3.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl3.SDL_EVENT_QUIT:
                running = False

        # Update the grid state
        grid = update_grid(grid)

        # Clear the screen (set to black)
        sdl3.SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255)
        sdl3.SDL_RenderClear(renderer)

        # Draw each live cell as a white rectangle
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if grid[y][x] == 1:
                    rect = sdl3.SDL_FRect()
                    rect.x = float(x * CELL_SIZE)
                    rect.y = float(y * CELL_SIZE)
                    rect.w = float(CELL_SIZE)
                    rect.h = float(CELL_SIZE)
                    sdl3.SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255)
                    sdl3.SDL_RenderFillRect(renderer, rect)

        # Present the rendered frame
        sdl3.SDL_RenderPresent(renderer)
        sdl3.SDL_Delay(100)  # Delay in milliseconds

    # Cleanup and quit
    sdl3.SDL_DestroyRenderer(renderer)
    sdl3.SDL_DestroyWindow(window)
    sdl3.SDL_Quit()

if __name__ == "__main__":
    main()

