# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import busio
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint

led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

#uart = busio.UART(board.TX, board.RX, baudrate=57600)

# If using with a computer such as Linux/RaspberryPi, Mac, Windows with USB/serial converter:
import serial
uart = serial. Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)

# If using with Linux/Raspberry Pi and hardware UART:
# import serial
# uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)

finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)


#For additional security, you can add timeout for a specific number of consecutive failed attempts
FAILED_ATTEMPTS_THRESHOLD = 4  # Set the number of failed attempts before timeout.
TIMEOUT_DURATION = 10  # Duration (in seconds) of timeout after exceeding failed attempts.

failed_attempts = 0  # Counter for consecutive failed attempts.


##################################################

def led_blink(rate=0.1, times=3):
    """Blink the LED based on rate and times specified."""
    for _ in range(times):
        led.value = True
        time.sleep(rate)
        led.value = False
        time.sleep(rate)

def get_fingerprint():
    """Get a finger print image, template it, and see if it matches!"""
    print("Waiting for image...")
    led_blink(rate=1, times=5)  # Blinking slowly indicating waiting for fingerprint.
    global failed_attempts  # Access the global counter.

    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        failed_attempts += 1  # Increment the failed attempt counter.
        led_blink()  # Blinking fast indicating an error.
        return handle_failed_attempts()
    print("Searching...")
    if finger.finger_search() != adafruit_fingerprint.OK:
        led_blink()  # Blinking fast indicating an error.
        return False
    led.value = True  # Lighting LED solid indicating successful detection.
    time.sleep(3)     # Keeping LED on for 3 seconds.
    led.value = False
    return True

#to keep track of the failed fingerprint attempts
def handle_failed_attempts():
    """Handles the scenario when there are multiple consecutive failed attempts."""
    global failed_attempts  # Access the global counter.
    if failed_attempts >= FAILED_ATTEMPTS_THRESHOLD:
        print(f"Too many failed attempts! Waiting for {TIMEOUT_DURATION} seconds.")
        led_blink(rate=0.5, times=5)  # Blinking to indicate lockout.
        time.sleep(TIMEOUT_DURATION)
        failed_attempts = 0  # Reset the counter after timeout.
        return False
    return False


# pylint: disable=too-many-branches
def get_fingerprint_detail():
    """Get a finger print image, template it, and see if it matches!
    This time, print out each error instead of just returning on failure"""
    print("Getting image...", end="")
    i = finger.get_image()
    if i == adafruit_fingerprint.OK:
        print("Image taken")
    else:
        if i == adafruit_fingerprint.NOFINGER:
            print("No finger detected")
        elif i == adafruit_fingerprint.IMAGEFAIL:
            print("Imaging error")
        else:
            print("Other error")
        return False

    print("Templating...", end="")
    i = finger.image_2_tz(1)
    if i == adafruit_fingerprint.OK:
        print("Templated")
    else:
        if i == adafruit_fingerprint.IMAGEMESS:
            print("Image too messy")
        elif i == adafruit_fingerprint.FEATUREFAIL:
            print("Could not identify features")
        elif i == adafruit_fingerprint.INVALIDIMAGE:
            print("Image invalid")
        else:
            print("Other error")
        return False

    print("Searching...", end="")
    i = finger.finger_fast_search()
    # pylint: disable=no-else-return
    # This block needs to be refactored when it can be tested.
    if i == adafruit_fingerprint.OK:
        print("Found fingerprint!")
        return True
    else:
        if i == adafruit_fingerprint.NOTFOUND:
            print("No match found")
        else:
            print("Other error")
        return False


# pylint: disable=too-many-statements
def enroll_finger(location):
    """Take a 2 finger images and template it, then store in 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...", end="")
        else:
            print("Place same finger again...", end="")

        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                led.value = True  # Lighting LED solid indicating successful enrollment.
                time.sleep(3)     # Keeping LED on for 3 seconds.
                led.value = False
                print("Image taken")
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="")
            elif i == adafruit_fingerprint.IMAGEFAIL:
                led_blink()  # Blinking fast indicating an error.
                print("Imaging error")
                return False
            else:
                led_blink()  # Blinking fast indicating an error.
                print("Other error")
                return False

        print("Templating...", end="")
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            led.value = True  # Lighting LED solid indicating successful enrollment.
            time.sleep(3)     # Keeping LED on for 3 seconds.
            led.value = False

        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Image too messy")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("Could not identify features")
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return False

        if fingerimg == 1:
            print("Remove finger")
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    print("Creating model...", end="")
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Created")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("Prints did not match")
        else:
            print("Other error")
        return False

    print("Storing model #%d..." % location, end="")
    i = finger.store_model(location)
    if i == adafruit_fingerprint.OK:
        print("Stored")
    else:
        if i == adafruit_fingerprint.BADLOCATION:
            print("Bad storage location")
        elif i == adafruit_fingerprint.FLASHERR:
            print("Flash storage error")
        else:
            print("Other error")
        return False

    return True


##################################################


def get_num():
    """Use input() to get a valid number from 1 to 127. Retry till success!"""
    i = 0
    while (i > 127) or (i < 1):
        try:
            i = int(input("Enter ID # from 1-127: "))
        except ValueError:
            pass
    return i


while True:
    print("----------------")
    if finger.read_templates() != adafruit_fingerprint.OK:
        raise RuntimeError("Failed to read templates")
    print("Fingerprint templates:", finger.templates)
    print("e) enroll print")
    print("f) find print")
    print("d) delete print")
    print("----------------")
    c = input("> ")

    if c == "e":
        enroll_finger(get_num())
    if c == "f":
        if get_fingerprint():
            print("Detected #", finger.finger_id, "with confidence", finger.confidence)
            failed_attempts = 0  # Reset the failed attempt counter on successful detection.
        else:
            print("Finger not found")
            led_blink()  # Blinking fast indicating an error.
    if c == "d":
        if finger.delete_model(get_num()) == adafruit_fingerprint.OK:
            print("Deleted!")
            led.value = True  # Lighting LED solid indicating successful deletion.
            time.sleep(3)     # Keeping LED on for 3 seconds.
            led.value = False
        else:
            print("Failed to delete")
            led_blink()  # Blinking fast indicating an error.
