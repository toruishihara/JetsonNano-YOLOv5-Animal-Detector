# gpio_blink.py
# Python 3.6 compatible

import time
import threading
import Jetson.GPIO as GPIO

RELAY1 = 29
RELAY2 = 31

BLINK_INTERVAL = 1.0    # seconds
TOTAL_SECONDS = 30.0

_gpio_thread = None
_gpio_lock = threading.Lock()
_gpio_running = False


def _gpio_worker():
    global _gpio_running

    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(RELAY1, GPIO.OUT, initial=GPIO.LOW)

        end_time = time.time() + TOTAL_SECONDS
        state = False

        while time.time() < end_time:
            state = not state
            GPIO.output(RELAY1, GPIO.HIGH if state else GPIO.LOW)
            time.sleep(BLINK_INTERVAL)

        GPIO.output(RELAY1, GPIO.LOW)

    except Exception as e:
        print("GPIO worker error:", e, flush=True)

    finally:
        GPIO.output(RELAY1, GPIO.LOW)
        with _gpio_lock:
            _gpio_running = False


def start_gpio_blink():
    """
    Start GPIO on/off every 2 sec for 60 sec.
    If already running, do nothing.
    """
    global _gpio_thread, _gpio_running

    with _gpio_lock:
        if _gpio_running:
            print("GPIO blink already running. Do nothing.", flush=True)
            return False

        _gpio_running = True
        _gpio_thread = threading.Thread(target=_gpio_worker)
        _gpio_thread.daemon = True
        _gpio_thread.start()

        print("GPIO blink started.", flush=True)
        return True


#if __name__ == "__main__":
#    start_gpio_blink()
#    time.sleep(1)
#    start_gpio_blink()
#    time.sleep(TOTAL_SECONDS + 3)
#    GPIO.cleanup()
#    print("Program ended", flush=True)
