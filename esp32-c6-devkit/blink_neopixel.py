import time
import machine
import neopixel

# Configuration
NEOPIXEL_PIN = 8  # GPIO on ESP32-C6
NUM_PIXELS = 1    # Number of neopixels
BRIGHTNESS = 0.2  # 20%

# Initialize NeoPixel
np = neopixel.NeoPixel(machine.Pin(NEOPIXEL_PIN), NUM_PIXELS)

def scale_color(color, brightness):
    return tuple(int(c * brightness) for c in color)

def blink(color, delay=0.5):
    np[0] = scale_color(color, BRIGHTNESS)
    np.write()
    time.sleep(delay)
    np[0] = (0, 0, 0)
    np.write()
    time.sleep(delay)

while True:
    blink((255, 0, 0))  # Red
    blink((0, 255, 0))  # Green
    blink((0, 0, 255))  # Blue

