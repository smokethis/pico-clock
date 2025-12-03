class WiFiManager:
    """Abstract base - defines the interface"""
    def connect(self, ssid, password):
        raise NotImplementedError
    
    def is_connected(self):
        raise NotImplementedError
    
    def get_ip(self):
        raise NotImplementedError


class PicoWWiFi(WiFiManager):
    """Native Pico W WiFi"""
    def __init__(self):
        import network
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
    
    def connect(self, ssid, password):
        self.wlan.connect(ssid, password)
        # Wait for connection
        import time
        max_wait = 10
        while max_wait > 0:
            if self.is_connected():
                return True
            max_wait -= 1
            time.sleep(1)
        return False
    
    def is_connected(self):
        return self.wlan.isconnected()
    
    def get_ip(self):
        return self.wlan.ifconfig()[0]