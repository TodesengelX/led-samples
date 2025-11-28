import time
import math
import random
import board
import adafruit_pixelbuf
from adafruit_raspberry_pi5_neopixel_write import neopixel_write

# Standard Animation Imports
from adafruit_led_animation.animation import Animation
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_led_animation.group import AnimationGroup
from adafruit_led_animation.helper import PixelSubset
from adafruit_led_animation.color import (
    RED, BLUE, PURPLE, JADE, GOLD, WHITE, BLACK, TEAL, MAGENTA
)
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.sparkle import Sparkle

# --- Configuration ---
NEOPIXEL_PIN = board.D18
NUM_PIXELS = 96
BRIGHTNESS = 0.6  # Cranked up a bit (watch your PSU!)

# --- HARDWARE DRIVER (Pi 5 Specific) ---
class Pi5Pixelbuf(adafruit_pixelbuf.PixelBuf):
    def __init__(self, pin, size, **kwargs):
        self._pin = pin
        super().__init__(size=size, **kwargs)

    def _transmit(self, buf):
        neopixel_write(self._pin, buf)

pixels = Pi5Pixelbuf(NEOPIXEL_PIN, NUM_PIXELS, auto_write=True, byteorder="BGR", brightness=BRIGHTNESS)

# --- CUSTOM ANIMATION 1: LiquidNeon (Math-based Plasma) ---
class LiquidNeon(Animation):
    def __init__(self, pixel_object, speed, color_a, color_b, period=5):
        super().__init__(pixel_object, speed, color_a)
        self.color_a = color_a
        self.color_b = color_b
        self.period = period
        self.offset = 0.0

    def draw(self):
        # Calculate a sine wave that moves over time
        self.offset += 0.2
        for i in range(len(self.pixel_object)):
            # Create a wave based on pixel position and time
            wave = math.sin(i * 0.2 + self.offset) + math.cos(i * 0.15 - self.offset)
            # Map wave (-2 to 2) to a mix of color_a and color_b
            mix = (wave + 2) / 4.0  # Normalize to 0.0 - 1.0
            
            # Manual color mixing (Linear Interpolation)
            r = int(self.color_a[0] * mix + self.color_b[0] * (1 - mix))
            g = int(self.color_a[1] * mix + self.color_b[1] * (1 - mix))
            b = int(self.color_a[2] * mix + self.color_b[2] * (1 - mix))
            
            self.pixel_object[i] = (r, g, b)

# --- CUSTOM ANIMATION 2: CyberGlitch (Randomized Corruption) ---
class CyberGlitch(Animation):
    def __init__(self, pixel_object, speed, color):
        super().__init__(pixel_object, speed, color)
        
    def draw(self):
        # 1. Randomly dim everything slightly (fade trail)
        for i in range(len(self.pixel_object)):
            current = self.pixel_object[i]
            # Fast fade (bit shift or multiply)
            self.pixel_object[i] = (int(current[0]*0.6), int(current[1]*0.6), int(current[2]*0.6))
            
        # 2. Inject random "glitches" (bright flashes)
        num_glitches = random.randint(1, 4)
        for _ in range(num_glitches):
            idx = random.randint(0, len(self.pixel_object) - 1)
            # Random bright color from a palette
            glitch_color = random.choice([WHITE, self.color, RED, (0, 255, 0)])
            self.pixel_object[idx] = glitch_color

# --- EFFECT SETUP ---

# 1. The "Collider" (Split Strip Logic)
# We split the strip in half. One comet goes up, one goes down.
half_point = NUM_PIXELS // 2
left_strip = PixelSubset(pixels, 0, half_point)
right_strip = PixelSubset(pixels, half_point, NUM_PIXELS)

# Left side: Red Comet moving forward
collider_left = Comet(left_strip, speed=0.02, color=RED, tail_length=15, bounce=True)
# Right side: Blue Comet moving backward (reverse=True doesn't exist on Comet, so we use logic or bounce)
# Actually, let's just use bounce on both for a "battle" look.
collider_right = Comet(right_strip, speed=0.02, color=BLUE, tail_length=15, bounce=True)

collision_event = AnimationGroup(collider_left, collider_right)

# 2. The Liquid Neon Instance
liquid_ooze = LiquidNeon(pixels, speed=0.01, color_a=PURPLE, color_b=TEAL)
liquid_fire = LiquidNeon(pixels, speed=0.01, color_a=RED, color_b=GOLD)

# 3. The Cyber Glitch Instance
matrix_glitch = CyberGlitch(pixels, speed=0.03, color=JADE)

# 4. High Speed Sparkle (Strobe)
panic_mode = Sparkle(pixels, speed=0.01, color=WHITE, num_sparkles=20)

# --- MASTER SEQUENCE ---
animations = AnimationSequence(
    liquid_ooze,        # 5 seconds of smooth purple/teal plasma
    collision_event,    # 5 seconds of Red/Blue comets hitting each other
    matrix_glitch,      # 5 seconds of digital rain/corruption
    liquid_fire,        # 5 seconds of molten gold/red plasma
    panic_mode,         # 5 seconds of intense white strobe
    advance_interval=5,
    auto_clear=True,
    random_order=False
)

print("Starting EXTREME Animation Sequence...")
print("Press Ctrl+C to stop.")

try:
    while True:
        animations.animate()
except KeyboardInterrupt:
    print("\nStopping...")
finally:
    pixels.fill(BLACK)
    pixels.show()