# scheduler.py
import json

class EventScheduler:
    def __init__(self, filename='events.json'):
        self.filename = filename
        self.events = self.load_events()
    
    def load_events(self):
        """Load events from JSON file"""
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except:
            # Default events if file doesn't exist
            return [
                {"time": "12:00", "name": "Lunch", "countdown": 5},
                {"time": "15:00", "name": "Afternoon Break", "countdown": 5}
            ]
    
    def save_events(self):
        """Save events to JSON file"""
        with open(self.filename, 'w') as f:
            json.dump(self.events, f)
    
    def add_event(self, time, name, countdown):
        """Add a new event"""
        self.events.append({"time": time, "name": name, "countdown": int(countdown)})
        self.events.sort(key=lambda e: e["time"])
        self.save_events()
    
    def remove_event(self, index):
        """Remove event by index"""
        if 0 <= index < len(self.events):
            del self.events[index]
            self.save_events()