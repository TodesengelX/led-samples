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

            # Diagnostic/test commands
            if s.lower() in ("test", "t"):
                run_hardware_test()
                continue

            if s.lower() in ("info", "i"):
                print(f"Pin object: {NEOPIXEL_PIN} (type: {type(NEOPIXEL_PIN)})")
                print(f"NUM_PIXELS={NUM_PIXELS}, auto_write={pixels.auto_write}")
                continue
            if s.lower() in ("order", "o"):
                test_byteorders()
                continue

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


def run_hardware_test():
    """Attempt basic hardware writes and report any exceptions."""
    print("Running hardware test: filling all LEDs white for 2 seconds...")
    try:
        # Try using PixelBuf API first
        pixels.fill((255, 255, 255))
        pixels.show()
        print("PixelBuf.fill/show succeeded (may be brightness-limited). Sleeping 2s...")
        time.sleep(2)
        pixels.fill(0)
        pixels.show()
        print("Cleared after PixelBuf test.")
    except Exception as e:
        print(f"PixelBuf write failed: {e}")

    # Try raw neopixel_write with a simple buffer
    try:
        print("Attempting raw neopixel_write with white buffer...")
        # Build minimal raw buffer: 3 bytes per pixel (RGB)
        raw = bytearray()
        for _ in range(NUM_PIXELS):
            raw += bytes((255, 255, 255))
        neopixel_write(NEOPIXEL_PIN, raw)
        print("neopixel_write(raw) succeeded.")
    except Exception as e:
        print(f"neopixel_write(raw) failed: {e}")


def test_byteorders():
    """Send visible test colors using different byte orders so you can identify the correct ordering.

    The function will send a red test pattern encoded for each candidate order and pause briefly.
    Observe which test shows a true red pixel; that's the correct byteorder for your strip.
    """
    def map_color_to_order(color, order):
        r, g, b = color
        mapping = {"R": r, "G": g, "B": b}
        return bytes((mapping[order[0]], mapping[order[1]], mapping[order[2]]))

    orders = ["GRB", "RGB", "BGR"]
    test_color = (255, 0, 0)  # target logical R=255

    print("\nByteorder diagnostic: for each test the first pixel should appear RED if ordering matches.")
    print("If you see GREEN or BLUE instead, note which ordering produced correct RED and we'll change byteorder accordingly.")

    for order in orders:
        try:
            print(f"Testing order {order} — sending RED encoded as {order}...")
            raw = bytearray()
            pix_bytes = map_color_to_order(test_color, order)
            for _ in range(NUM_PIXELS):
                raw += pix_bytes
            neopixel_write(NEOPIXEL_PIN, raw)
            time.sleep(1.2)
            # clear quickly
            neopixel_write(NEOPIXEL_PIN, bytearray([0]) * (NUM_PIXELS * 3))
            time.sleep(0.2)
        except Exception as e:
            print(f"Error writing test for {order}: {e}")

    print("Byteorder tests finished. Use the ordering that displayed RED correctly.")
    print("If none looked correct, check wiring, ground, level shifter, and power supply.")

    print("\nQuick troubleshooting checklist:")
    print("- Ensure 5V supply can source enough current and is connected to the LED strip's +5V and GND.")
    print("- Ensure Pi ground and strip ground are common (connected).")
    print("- Add a 1000uF capacitor across +5V and GND at the strip input to prevent voltage sag.")
    print("- Put a ~300-470 ohm resistor in series with the data line close to the first LED to reduce ringing.")
    print("- For the 74AHCT125 level shifter: power it from +5V, ensure its output-enable (/OE) pins are set to enable outputs per the datasheet, and tie any unused OE inputs to the enabled state.")
    print("- If colors stay wrong or change when multiple LEDs are lit, suspect timing/signal integrity or power sag — verify with the 'test' command and a multimeter.")


if __name__ == "__main__":
    interactive_console()