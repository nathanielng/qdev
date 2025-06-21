import json
import hashlib
import pyperclip
import threading
import time

from datetime import datetime
from pathlib import Path

JSON_FILE = 'clipboard_history.json'
TXT_FILE = 'clipboard_history.txt'

class RobustClipboardMonitor:
    def __init__(self, max_history=1000, json_file=JSON_FILE, txt_file=TXT_FILE):
        self.history = []
        self.content_hashes = set()
        self.max_history = max_history
        self.json_file = json_file
        self.txt_file = txt_file
        self.running = False
        self.last_content = ""
        self.load_existing_history()
    
    def load_existing_history(self):
        if Path(self.json_file).exists():
            try:
                with open(self.json_file, 'r') as f:
                    self.history = json.load(f)
                    for entry in self.history:
                        if 'hash' in entry:
                            self.content_hashes.add(entry['hash'])
                print(f"Loaded {len(self.history)} existing entries")
            except Exception as e:
                print(f"Error loading history: {e}")
    
    def is_duplicate(self, content):
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return content_hash in self.content_hashes
    
    def add_to_history(self, content):
        if self.is_duplicate(content):
            return False
        
        content_hash = hashlib.md5(content.encode()).hexdigest()
        self.content_hashes.add(content_hash)
        
        entry = {
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'hash': content_hash,
            'length': len(content)
        }
        
        self.history.append(entry)
        
        if len(self.history) > self.max_history:
            removed = self.history.pop(0)
            if 'hash' in removed:
                self.content_hashes.discard(removed['hash'])
        
        return True
    
    def monitor_loop(self):
        # Get initial clipboard content
        try:
            self.last_content = pyperclip.paste()
        except:
            self.last_content = ""
        
        while self.running:
            try:
                current_content = pyperclip.paste()
                
                if (current_content != self.last_content and 
                    current_content and 
                    current_content.strip()):
                    
                    if current_content.startswith("https://"):
                        if self.add_to_history(current_content):
                            print(f"New content: {current_content[:50]}...")
                            self.save_history()                
                time.sleep(0.5)  # Check every 500ms
                
            except Exception as e:
                print(f"Error reading clipboard: {e}")
                time.sleep(1)  # Wait longer on error
    
    def start_monitoring(self):
        self.running = True
        monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        monitor_thread.start()
        
        print("Clipboard monitoring started... Press Ctrl+C to stop")
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        self.running = False
        self.save_history()
        print(f"\nMonitoring stopped. Total entries: {len(self.history)}")
    
    def save_history(self):
        try:
            # Save JSON version
            with open(self.json_file, 'w') as f:
                json.dump(self.history, f, indent=2)
            
            # Save TXT version
            with open(self.txt_file, 'w') as f:
                for entry in self.history:
                    if entry['content'].startswith('https://'):
                        f.write(f"{entry['content']}\n")
                    
        except Exception as e:
            print(f"Error saving history: {e}")

# Usage
if __name__ == "__main__":
    monitor = RobustClipboardMonitor()
    monitor.start_monitoring()
