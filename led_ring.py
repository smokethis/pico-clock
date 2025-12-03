# led_ring.py
import neopixel
from machine import Pin

class LEDRing:
    def __init__(self, pin, num_leds):
        self.ring = neopixel.NeoPixel(Pin(pin), num_leds)
        self.num_leds = num_leds
    
    def show_countdown(self, progress, color=(255, 0, 0)):
        """Progress from 0.0 to 1.0"""
        num_lit = int(self.num_leds * progress)
        for i in range(self.num_leds):
            if i < num_lit:
                self.ring[i] = color
            else:
                self.ring[i] = (0, 0, 0)
        self.ring.write()
    
    def show_clock(self, hour_fraction):
        """Show single LED as clock hand"""
        self.ring.fill((0, 0, 0))
        led = int(self.num_leds * hour_fraction) % self.num_leds
        self.ring[led] = (0, 20, 0)
        self.ring.write()
    
    def fill(self, color):
        """Set all LEDs to one color"""
        self.ring.fill(color)
        self.ring.write()