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

# --- HARDWARE DRIVER ---
class Pi5Pixelbuf(adafruit_pixelbuf.PixelBuf):
    def __init__(self, pin, size, **kwargs):
        self._pin = pin
        super().__init__(size=size, **kwargs)

    def _transmit(self, buf):
        neopixel_write(self._pin, buf)

# --- THE FIX IS HERE ---
# 1. auto_write=False: Don't send data immediately when we change a pixel.
pixels = Pi5Pixelbuf(NEOPIXEL_PIN, NUM_PIXELS, auto_write=False, byteorder="BGR", brightness=BRIGHTNESS)

# --- CUSTOM ANIMATION ---
class Static3rdLed(Animation):
    def __init__(self, pixel_object, color):
        # We set speed=1.0 because we don't need to refresh this fast. 
        # It's a static image.
        super().__init__(pixel_object, speed=1.0, color=color)

    def draw(self):
        # 2. Fill the buffer in MEMORY (The LEDs don't know this is happening yet)
        self.pixel_object.fill(BLACK)
        
        for i in range(0, len(self.pixel_object), 3):
            self.pixel_object[i] = self.color
            
        # 3. Send the ONE clean signal to the strip
        self.pixel_object.show()

static_white = Static3rdLed(pixels, color=WHITE)
animations = AnimationSequence(static_white)

print("Displaying Every 3rd LED (Buffered Mode)...")

try:
    while True:
        animations.animate()
except KeyboardInterrupt:
    print("\nStopping...")
    pixels.fill(BLACK)
    pixels.show()