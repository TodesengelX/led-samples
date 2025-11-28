import time
import board
import adafruit_pixelbuf
from adafruit_raspberry_pi5_neopixel_write import neopixel_write

# We use the Animation library because we KNOW it works on your hardware
from adafruit_led_animation.animation import Animation
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_led_animation.color import WHITE, BLACK

# --- Configuration ---
NEOPIXEL_PIN = board.D13
NUM_PIXELS = 96
BRIGHTNESS = 0.5 

# --- HARDWARE DRIVER (The Working Pi 5 Driver) ---
class Pi5Pixelbuf(adafruit_pixelbuf.PixelBuf):
    def __init__(self, pin, size, **kwargs):
        self._pin = pin
        super().__init__(size=size, **kwargs)

    def _transmit(self, buf):
        neopixel_write(self._pin, buf)

# Initialize exactly like the working script
pixels = Pi5Pixelbuf(NEOPIXEL_PIN, NUM_PIXELS, auto_write=True, byteorder="BGR", brightness=BRIGHTNESS)

# --- CUSTOM "ANIMATION" FOR STATIC LIGHTS ---
# We treat the static lights as an animation that just redraws the same thing.
# This ensures the timing matches the working script perfectly.
class Static3rdLed(Animation):
    def __init__(self, pixel_object, color):
        # speed=0.1 means it refreshes 10 times a second (safe speed)
        super().__init__(pixel_object, speed=0.1, color=color)

    def draw(self):
        # Clear everything first to be safe
        self.pixel_object.fill(BLACK)
        
        # Turn on every 3rd pixel
        for i in range(0, len(self.pixel_object), 3):
            self.pixel_object[i] = self.color

# Create the "Animation"
static_white = Static3rdLed(pixels, color=WHITE)

# Use the Sequence manager to run it
# This handles the loop and timing for us
animations = AnimationSequence(static_white)

print("Displaying Every 3rd LED (Animation Mode)...")

try:
    while True:
        animations.animate()
except KeyboardInterrupt:
    print("\nStopping...")
    pixels.fill(BLACK)
    pixels.show()