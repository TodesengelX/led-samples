import time
import board
import adafruit_pixelbuf
from adafruit_raspberry_pi5_neopixel_write import neopixel_write

# --- Configuration ---
NEOPIXEL_PIN = board.D18
NUM_PIXELS = 96
BRIGHTNESS = 1.0  # Full brightness as requested (Caution: High Amp Draw)
COLOR_WHITE = (255, 255, 255)

# --- HARDWARE DRIVER (Pi 5 Specific) ---
class Pi5Pixelbuf(adafruit_pixelbuf.PixelBuf):
    def __init__(self, pin, size, **kwargs):
        self._pin = pin
        super().__init__(size=size, **kwargs)

    def _transmit(self, buf):
        neopixel_write(self._pin, buf)

# Initialize
pixels = Pi5Pixelbuf(NEOPIXEL_PIN, NUM_PIXELS, auto_write=False, byteorder="BGR", brightness=BRIGHTNESS)

print("Clearing strip...")
pixels.fill((0, 0, 0))

print("Setting every 3rd LED to Full White...")