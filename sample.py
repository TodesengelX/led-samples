import time
import board
import adafruit_pixelbuf
from adafruit_raspberry_pi5_neopixel_write import neopixel_write

# --- Configuration ---
NEOPIXEL_PIN = board.D18  # Data pin
NUM_PIXELS = 96           # Number of LEDs (adjust to your strip)
BRIGHTNESS = 0.5          # 0.0 to 1.0


# --- Raspberry Pi 5 Custom PixelBuf Driver ---
class Pi5Pixelbuf(adafruit_pixelbuf.PixelBuf):
    def __init__(self, pin, size, **kwargs):
        self._pin = pin
        super().__init__(size=size, **kwargs)

    def _transmit(self, buf):
        neopixel_write(self._pin, buf)


# Initialize the pixel strip with manual writes so we control when updates happen
pixels = Pi5Pixelbuf(NEOPIXEL_PIN, NUM_PIXELS, auto_write=False, byteorder="BGR", brightness=BRIGHTNESS)


def light_single_led(one_based_index, color=(255, 255, 255)):
    """Turn off all LEDs and light a single LED (1-based index).

    Raises ValueError for out-of-range indices.
    """
    idx = one_based_index - 1
    if idx < 0 or idx >= NUM_PIXELS:
        raise ValueError("LED index out of range")

    # Clear all, set the requested LED, then transmit
    pixels.fill(0)
    pixels[idx] = color
    pixels.show()


def interactive_console():
    print(f"Interactive LED console — pin: D18, LEDs: {NUM_PIXELS}")
    print("Enter a number 1..{0} to light that LED, or 'q' to quit.".format(NUM_PIXELS))

    # Start with all LEDs off
    pixels.fill(0)
    pixels.show()

    current = None
    try:
        while True:
            s = input(f"LED number (1-{NUM_PIXELS}) or 'q' to quit: ").strip()
            if not s:
                continue
            if s.lower() in ("q", "quit", "exit"):
                break

            try:
                n = int(s)
            except ValueError:
                print("Please enter a valid integer or 'q' to quit.")
                continue

            if n < 1 or n > NUM_PIXELS:
                print(f"Out of range — enter a number between 1 and {NUM_PIXELS}.")
                continue

            try:
                light_single_led(n)
                current = n
                print(f"Lit LED {n}.")
            except Exception as e:
                print(f"Failed to set LED: {e}")

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        # Ensure we clear the strip on exit
        try:
            pixels.fill(0)
            pixels.show()
            print("LEDs cleared.")
        except Exception:
            print("Could not clear LEDs (hardware may be absent).")


if __name__ == "__main__":
    interactive_console()