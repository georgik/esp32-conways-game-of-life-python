import os
import select
import ctypes
import sdl3

# Path to the named pipe (FIFO). Change this to "/dev/leds0" if needed.
PIPE_PATH = "/tmp/leds0"

# SDL3 window dimensions
WIDTH, HEIGHT = 800, 600

def init_sdl():
    if not sdl3.SDL_Init(sdl3.SDL_INIT_VIDEO):
        print("SDL could not initialize:", sdl3.SDL_GetError().decode())
        return None, None

    window = sdl3.SDL_CreateWindow(
        b"Kirby Simulator",
        WIDTH, HEIGHT,
        sdl3.SDL_WINDOW_RESIZABLE
    )
    if not window:
        print("Window could not be created:", sdl3.SDL_GetError().decode())
        sdl3.SDL_Quit()
        return None, None

    renderDrivers = [sdl3.SDL_GetRenderDriver(i).decode() for i in range(sdl3.SDL_GetNumRenderDrivers())]
    try_get_driver = lambda order, drivers: next((i for i in order if i in drivers), None)
    render_driver = try_get_driver(["opengl", "software"], renderDrivers)
    if render_driver:
        render_driver = render_driver.encode()
    else:
        render_driver = None

    renderer = sdl3.SDL_CreateRenderer(window, render_driver)
    if not renderer:
        print("Renderer creation failed:", sdl3.SDL_GetError().decode())
        sdl3.SDL_DestroyWindow(window)
        sdl3.SDL_Quit()
        return None, None

    return window, renderer

def init_pipe(path=PIPE_PATH):
    """Creates a named pipe if it doesn't exist and opens it for nonblocking reading."""
    if not os.path.exists(path):
        os.mkfifo(path)
        print(f"Created FIFO at {path}")
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    print(f"Opened FIFO for reading: {path}")
    return fd

def parse_led_data(data: bytes):
    """
    Parse raw binary data into a list of (r, g, b) color tuples.
    
    Assumes each LED is represented by 4 bytes (little-endian):
      - Byte 0: blue
      - Byte 1: green
      - Byte 2: red
      - Byte 3: unused
    """
    colors = []
    num_leds = len(data) // 4
    for i in range(num_leds):
        chunk = data[i*4:(i+1)*4]
        blue = chunk[0]
        green = chunk[1]
        red = chunk[2]
        colors.append((red, green, blue))
    return colors

def main():
    window, renderer = init_sdl()
    if not window or not renderer:
        return

    pipe_fd = init_pipe()
    # current_frame will hold the latest list of LED colors.
    current_frame = None

    running = True
    event = sdl3.SDL_Event()

    while running:
        # Process SDL events.
        while sdl3.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl3.SDL_EVENT_QUIT:
                running = False

        # Poll the FIFO for data.
        rlist, _, _ = select.select([pipe_fd], [], [], 0)
        if rlist:
            try:
                data = os.read(pipe_fd, 4096)
                if not data:
                    print("Writer closed pipe; reopening...")
                    os.close(pipe_fd)
                    pipe_fd = init_pipe()
                else:
                    # Parse the incoming binary data into LED color tuples.
                    current_frame = parse_led_data(data)
            except BlockingIOError:
                pass

        # Render the LED matrix.
        sdl3.SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255)
        sdl3.SDL_RenderClear(renderer)
         gamma = 60

        if current_frame and len(current_frame) >= 64:
            # Use the first 64 LEDs to form an 8x8 matrix.
            matrix_leds = current_frame[:64]
            cell_width = WIDTH / 8
            cell_height = HEIGHT / 8
            for row in range(8):
                for col in range(8):
                    index = row * 8 + col
                    r, g, b = matrix_leds[index]
                    rect = sdl3.SDL_FRect()
                    rect.x = col * cell_width
                    rect.y = row * cell_height
                    rect.w = cell_width
                    rect.h = cell_height
                    sdl3.SDL_SetRenderDrawColor(renderer, (r + gamma) % 255, (g + gamma) % 255, (b + gamma) %255, 255)
                    sdl3.SDL_SetRenderDrawColor(renderer, r, g, b, 255)
                    sdl3.SDL_RenderFillRect(renderer, rect)
        else:
            # Optionally render a placeholder if no frame is available.
            pass

        sdl3.SDL_RenderPresent(renderer)
        sdl3.SDL_Delay(16)  # Roughly 60 FPS

    # Cleanup
    sdl3.SDL_DestroyRenderer(renderer)
    sdl3.SDL_DestroyWindow(window)
    sdl3.SDL_Quit()
    os.close(pipe_fd)

if __name__ == "__main__":
    main()

