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
BRIGHTNESS = 0.5 

# --- HARDWARE DRIVER (The one we know works) ---
class Pi5Pixelbuf(adafruit_pixelbuf.PixelBuf):
    def __init__(self, pin, size, **kwargs):
        self._pin = pin
        super().__init__(size=size, **kwargs)

    def _transmit(self, buf):
        neopixel_write(self._pin, buf)

# --- CRITICAL SETTING ---
# auto_write=False is the secret. It prevents the "Green/Yellow" data crash.
pixels = Pi5Pixelbuf(NEOPIXEL_PIN, NUM_PIXELS, auto_write=False, byteorder="BGR", brightness=BRIGHTNESS)

# --- YOUR CUSTOM PATTERN LOGIC ---
class MySpecificLights(Animation):
    def __init__(self, pixel_object, color):
        # Refresh rate of 1.0 second. We don't need speed, we need stability.
        super().__init__(pixel_object, speed=1.0, color=color)

    def draw(self):
        # 1. Wipe the slate clean (in memory)
        self.pixel_object.fill(BLACK)
        
        # 2. Apply the "Every 3rd LED" rule first
        # Range(start, stop, step) -> 0, 3, 6, 9, 12, 15...
        for i in range(0, 96, 3):
             self.pixel_object[i] = WHITE
             
        # 3. Apply your Specific Overrides
        # You wanted: 1st, 3rd, 7th, 10th
        
        # 1st LED is index 0 (Already covered by loop, but let's be sure)
        self.pixel_object[0] = WHITE
        
        # 3rd LED is index 2 (This is the tricky one not in the loop!)
        self.pixel_object[2] = WHITE
        
        # 7th LED is index 6 (Already in loop, but forcing it just in case)
        self.pixel_object[6] = WHITE
        
        # 10th LED is index 9 (Already in loop)
        self.pixel_object[9] = WHITE

        # 4. SEND THE DATA
        # This sends one perfect, clean signal to the strip. No confusion.
        self.pixel_object.show()

# Setup the animation sequence
custom_pattern = MySpecificLights(pixels, color=WHITE)
animations = AnimationSequence(custom_pattern)

print("Displaying Custom Pattern: 1st, 3rd, 7th, 10th + Every 3rd...")
print("Press Ctrl+C to stop.")

try:
    while True:
        # This keeps the signal alive and stable
        animations.animate()
except KeyboardInterrupt:
    print("\nStopping...")
    pixels.fill(BLACK)
    pixels.show()