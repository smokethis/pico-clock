# clock_app.py
import asyncio
import time
import ntptime
from led_ring import LEDRing
from scheduler import EventScheduler
from wifi_manager import PicoWWiFi
from config import *

class TimeCountdownApp:
    def __init__(self):
        self.wifi = PicoWWiFi()
        self.ring = LEDRing(LED_RING_PIN, LED_RING_COUNT)
        self.scheduler = EventScheduler()
    
    def time_to_minutes(self, time_str):
        """Convert 'HH:MM' to minutes since midnight"""
        h, m = map(int, time_str.split(':'))
        return h * 60 + m
    
    def get_next_event(self):
        """Find the next upcoming event"""
        t = time.localtime()
        current_minutes = t[3] * 60 + t[4]
        
        for event in self.scheduler.events:
            event_minutes = self.time_to_minutes(event['time'])
            if event_minutes > current_minutes:
                return event, event_minutes
        
        # Wrap to tomorrow - first event
        if self.scheduler.events:
            event = self.scheduler.events[0]
            return event, self.time_to_minutes(event['time']) + 1440
        
        return None, None
    
    async def update_display_loop(self):
        """Main display loop - runs every second"""
        while True:
            t = time.localtime()
            current_minutes = t[3] * 60 + t[4]
            
            event, event_time = self.get_next_event()
            
            if event:
                time_until = event_time - current_minutes
                countdown_minutes = event['countdown']
                
                if 0 <= time_until <= countdown_minutes:
                    # Countdown active!
                    progress = 1 - (time_until / countdown_minutes)
                    print(f"Countdown: {event['name']} - {progress:.2%}")
                    #self.ring.show_countdown(progress)
                else:
                    # Show clock in ambient mode
                    print(f"No events scheduled. The time is currently: {t}")
                    hour_fraction = (current_minutes % 720) / 720
                    #self.ring.show_clock(hour_fraction)
            
            await asyncio.sleep(1)
    
    async def handle_client(self, reader, writer):
        """Handle HTTP request"""
        try:
            request_line = await reader.readline()
            request = request_line.decode().strip()
            
            # Read headers
            while True:
                line = await reader.readline()
                if line == b'\r\n':
                    break
            
            # Route requests
            if 'GET / ' in request or 'GET /index' in request:
                # Serve index.html
                try:
                    with open('www/index.html', 'r') as f:
                        html = f.read()
                    writer.write(b'HTTP/1.1 200 OK\r\n')
                    writer.write(b'Content-Type: text/html\r\n')
                    writer.write(b'\r\n')
                    writer.write(html.encode())
                except OSError:
                    writer.write(b'HTTP/1.1 500 Internal Server Error\r\n\r\n')
                    writer.write(b'Could not load index.html')
            
            elif 'GET /api/events' in request:
                # JSON API endpoint
                import json
                events_json = json.dumps(self.scheduler.events)
                writer.write(b'HTTP/1.1 200 OK\r\n')
                writer.write(b'Content-Type: application/json\r\n')
                writer.write(b'\r\n')
                writer.write(events_json.encode())
            
            elif 'POST /add' in request:
                # Handle adding events (we'll come back to this)
                writer.write(b'HTTP/1.1 200 OK\r\n\r\nEvent added!')
            
            else:
                writer.write(b'HTTP/1.1 404 Not Found\r\n\r\n404 Not Found')
            
            await writer.drain()
        except Exception as e:
            print(f"Request error: {e}")
            import sys
            sys.print_exception(e)
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def web_server(self):
        await asyncio.start_server(
            self.handle_client,
            "0.0.0.0",
            WEB_SERVER_PORT
        )
        
        print(f'Web server: http://{self.wifi.get_ip()}/')
        
        # Just wait forever - the server keeps running
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour, repeat forever
    
    async def run(self):
        """Main entry point"""
        # Connect WiFi
        print("Connecting to WiFi...")
        if not self.wifi.connect(WIFI_SSID, WIFI_PASSWORD):
            print("WiFi connection failed!")
            return
        
        print(f"Connected: {self.wifi.get_ip()}")
        
        # Sync time
        print("Syncing time...")
        try:
            ntptime.host = NTP_SERVER
            ntptime.settime()
            print(f"Time synced: {time.localtime()}")
        except Exception as e:
            print(f"NTP sync failed: {e}")
            return
        
        # Show ready status
        self.ring.fill((0, 20, 0))  # Dim green
        
        # Run everything
        print("Starting main loops...")
        await asyncio.gather(
            self.update_display_loop(),
            self.web_server()
        )