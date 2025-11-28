import time
import board
import adafruit_pixelbuf
from adafruit_raspberry_pi5_neopixel_write import neopixel_write

# --- Configuration ---
NEOPIXEL_PIN = board.D13
NUM_PIXELS = 96
BRIGHTNESS = 0.5  # Lowered to 0.5 to match the working script and prevent voltage crash
COLOR_WHITE = (255, 255, 255)

# --- HARDWARE DRIVER (Copying the EXACT class from the working script) ---
class Pi5Pixelbuf(adafruit_pixelbuf.PixelBuf):
    def __init__(self, pin, size, **kwargs):
        self._pin = pin
        super().__init__(size=size, **kwargs)

    def _transmit(self, buf):
        neopixel_write(self._pin, buf)

# --- THE FIX: Change auto_write to True ---
# We use auto_write=True because we know this worked in the previous script.
pixels = Pi5Pixelbuf(NEOPIXEL_PIN, NUM_PIXELS, auto_write=True, byteorder="BGR", brightness=BRIGHTNESS)

print("Running Loop... Press Ctrl+C to stop.")

try:
    while True:
        # We put the setting inside the loop. 
        # Even though we are setting the same color over and over, 
        # this forces the Pi to continuously send the data signal.
        # This fixes the "Single Shot" issue where Linux might interrupt the signal.
        
        for i in range(0, NUM_PIXELS, 3):
            pixels[i] = COLOR_WHITE
        
        # Add a small sleep to prevent CPU overheating, but keep it fast
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nStopping...")
    pixels.fill((0, 0, 0))
    # No need to call .show() because auto_write is True