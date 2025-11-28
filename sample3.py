import time
import board
import adafruit_pixelbuf
from adafruit_raspberry_pi5_neopixel_write import neopixel_write
from adafruit_led_animation.animation import Animation
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_led_animation.color import WHITE, BLACK

# --- Configuration ---
NEOPIXEL_PIN = board.D13
NUM_PIXELS = 96
# We set brightness lower to prevent "Yellowing" (voltage drop) 
# and ensure the data signal stays strong.
BRIGHTNESS = 0.3 

# --- DRIVER (EXACTLY AS IT WAS IN THE WORKING SCRIPT) ---
class Pi5Pixelbuf(adafruit_pixelbuf.PixelBuf):
    def __init__(self, pin, size, **kwargs):
        self._pin = pin
        super().__init__(size=size, **kwargs)

    def _transmit(self, buf):
        neopixel_write(self._pin, buf)

# We use auto_write=True because this was the setting in the script that WORKED.
# We will manage the "flood" of data by using a slow animation speed.
pixels = Pi5Pixelbuf(NEOPIXEL_PIN, NUM_PIXELS, auto_write=True, byteorder="BGR", brightness=BRIGHTNESS)

# --- CUSTOM LOGIC ---
class SpecificPattern(Animation):
    def __init__(self, pixel_object):
        # speed=0.5 means it refreshes every half second. 
        # This prevents the "Green/Yellow" data flood.
        super().__init__(pixel_object, speed=0.5, color=WHITE)

    def draw(self):
        # 1. Clear everything (Black)
        self.pixel_object.fill(BLACK)
        
        # 2. Set "Every 3rd LED" (0, 3, 6, 9, 12...)
        # We step by 3.
        for i in range(0, 96, 3):
            self.pixel_object[i] = WHITE
            
        # 3. Add your specific overrides
        # 1st LED (Index 0) - Already done by loop, but we ensure it.
        self.pixel_object[0] = WHITE
        
        # 3rd LED (Index 2) - This is the odd one out!
        self.pixel_object[2] = WHITE
        
        # 7th LED (Index 6) - Already done by loop (3, 6).
        self.pixel_object[6] = WHITE
        
        # 10th LED (Index 9) - Already done by loop (3, 6, 9).
        self.pixel_object[9] = WHITE

# Initialize the animation
pattern = SpecificPattern(pixels)
animations = AnimationSequence(pattern)

print("Displaying Pattern: 1, 3, 7, 10 + Every 3rd.")
print("Using 'Extreme' Engine for stability.")
print("Press Ctrl+C to stop.")

try:
    while True:
        animations.animate()
except KeyboardInterrupt:
    print("\nStopping...")
    pixels.fill(BLACK)