import time
import board
import adafruit_pixelbuf
from adafruit_raspberry_pi5_neopixel_write import neopixel_write

# Import ALL the animations and colors for maximum chaos
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.colorcycle import ColorCycle
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.rainbowchase import RainbowChase
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_led_animation.group import AnimationGroup
from adafruit_led_animation.color import (
    AMBER, AQUA, BLUE, CYAN, GOLD, GREEN, JADE, MAGENTA, 
    ORANGE, PINK, PURPLE, RED, TEAL, WHITE, YELLOW, RAINBOW
)

# --- Configuration ---
NEOPIXEL_PIN = board.D13  # Connected to GPIO 13
NUM_PIXELS = 96           # Number of LEDs
BRIGHTNESS = 0.5          # 0.0 to 1.0 (Watch your power supply current!)

# --- Raspberry Pi 5 Custom PixelBuf Driver ---
class Pi5Pixelbuf(adafruit_pixelbuf.PixelBuf):
    def __init__(self, pin, size, **kwargs):
        self._pin = pin
        super().__init__(size=size, **kwargs)

    def _transmit(self, buf):
        neopixel_write(self._pin, buf)

# Initialize the pixel strip
pixels = Pi5Pixelbuf(NEOPIXEL_PIN, NUM_PIXELS, auto_write=True, byteorder="BGR", brightness=BRIGHTNESS)

# --- Define Extreme Animations ---

# 1. High-Speed Rainbow Effects
fast_rainbow = Rainbow(pixels, speed=0.01, period=2)
hyper_chase = RainbowChase(pixels, speed=0.01, size=5, spacing=2, step=4)
crazy_comet = RainbowComet(pixels, speed=0.01, tail_length=20, bounce=True)

# 2. Layered Chaos (Groups)
# Combining a pulsing background with sparkles on top
pulsing_background = Pulse(pixels, speed=0.05, color=BLUE, period=2)
white_sparkles = Sparkle(pixels, speed=0.02, color=WHITE, num_sparkles=10)
sparkle_pulse_group = AnimationGroup(pulsing_background, white_sparkles)

# 3. "Police" Strobe Effect
police_blink_red = Blink(pixels, speed=0.1, color=RED)
police_blink_blue = Blink(pixels, speed=0.1, color=BLUE)

# 4. Matrix-style Digital Rain (Green Comet with heavy tail)
matrix_rain = Comet(pixels, speed=0.02, color=JADE, tail_length=15, bounce=False)

# 5. The "Fire" Chase
fire_chase = Chase(pixels, speed=0.03, color=RED, size=2, spacing=1)
ember_sparkle = Sparkle(pixels, speed=0.05, color=AMBER, num_sparkles=5)
fire_storm = AnimationGroup(fire_chase, ember_sparkle)

# 6. Random Color Cycling Strobe
disco_party = ColorCycle(pixels, speed=0.1, colors=[MAGENTA, CYAN, YELLOW, PURPLE, JADE, ORANGE])

# 7. Intense Sparkle Storm
stormy = Sparkle(pixels, speed=0.01, color=TEAL, num_sparkles=25)

# --- The Master Sequence ---
animations = AnimationSequence(
    fast_rainbow,           # 0. Smooth rainbow
    sparkle_pulse_group,    # 1. Blue pulse with white sparkles
    hyper_chase,            # 2. Fast rainbow chase
    fire_storm,             # 3. Red chase with amber sparkles
    crazy_comet,            # 4. Bouncing rainbow comet
    disco_party,            # 5. Rapid color cycling
    matrix_rain,            # 6. Green trail
    stormy,                 # 7. Intense teal sparkles
    
    advance_interval=4,     # Switch every 4 seconds
    auto_clear=True,        # Clear LEDs between modes
    random_order=True,      # Randomize the order for maximum craziness
)

print("Starting EXTREME Animation Sequence...")

try:
    while True:
        animations.animate()
except KeyboardInterrupt:
    print("\nStopping...")
finally:
    pixels.fill(0)
    pixels.show()
    print("LEDs cleared.")