import time
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

# Configuration
WATCH_FOLDER = "/home/manuel/accion_new/Talk"
TEMP_FOLDER = "data/temp"
TRIGGER_PREFIX = "blog_"
SUPPORTED_FORMATS = ['.wav', '.mp3', '.m4a']

class AudioFileHandler(FileSystemEventHandler):
    def __init__(self):
        # Ensure temp folder exists
        os.makedirs(TEMP_FOLDER, exist_ok=True)
    
    def on_created(self, event):
        """Handle new file creation"""
        print(f"🔍 DEBUG: File CREATED: {event.src_path}")
        self.handle_file_event(event.src_path, "CREATED")
    
    def on_moved(self, event):
        """Handle file moves/renames (Nextcloud often does this)"""
        print(f"🔍 DEBUG: File MOVED: {event.src_path} -> {event.dest_path}")
        self.handle_file_event(event.dest_path, "MOVED")
    
    def on_modified(self, event):
        """Handle file modifications"""
        print(f"🔍 DEBUG: File MODIFIED: {event.src_path}")
        self.handle_file_event(event.src_path, "MODIFIED")
    
    def handle_file_event(self, file_path, event_type):
        """Common handler for all file events"""
        if os.path.isdir(file_path):
            print(f"🔍 DEBUG: Ignoring directory: {file_path}")
            return
            
        filename = os.path.basename(file_path)
        print(f"🔍 DEBUG: Checking {event_type} file: {filename}")
        
        if self.should_process_file(filename):
            print(f"🎵 {event_type} audio file detected: {filename}")
            # Wait a moment for file to finish copying/syncing
            time.sleep(3)
            self.process_audio_file(file_path, filename)
        else:
            print(f"🔍 DEBUG: File {filename} does not match criteria")
    
    def should_process_file(self, filename):
        """Check if file should trigger processing"""
        name_lower = filename.lower()
        
        print(f"🔍 DEBUG: Filename lower: '{name_lower}'")
        
        # Skip Nextcloud temporary files
        if filename.startswith('.') or '~' in filename or filename.endswith('.tmp'):
            print(f"🔍 DEBUG: Skipping temp/hidden file: {filename}")
            return False
        
        print(f"🔍 DEBUG: Starts with '{TRIGGER_PREFIX}': {name_lower.startswith(TRIGGER_PREFIX)}")
        
        # Check prefix and extension
        has_trigger = name_lower.startswith(TRIGGER_PREFIX)
        has_supported_ext = any(name_lower.endswith(ext) for ext in SUPPORTED_FORMATS)
        
        print(f"🔍 DEBUG: Has supported extension: {has_supported_ext}")
        
        return has_trigger and has_supported_ext
    
    def process_audio_file(self, source_path, filename):
        """Process the audio file through our pipeline"""
        try:
            print(f"📂 Processing: {filename}")
            
            # Step 1: Copy to temp folder
            temp_path = os.path.join(TEMP_FOLDER, filename)
            shutil.copy2(source_path, temp_path)
            print(f"✅ Copied to temp: {temp_path}")
            
            # Step 2: Process through pipeline (placeholder for now)
            self.run_processing_pipeline(temp_path, filename)
            
            # Step 3: Cleanup - delete both files
            os.remove(source_path)  # Delete from Talk folder
            os.remove(temp_path)    # Delete from temp folder
            print(f"🗑️ Cleaned up files for: {filename}")
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
    
    def run_processing_pipeline(self, audio_path, filename):
        """Run the full processing pipeline"""
        print(f"🔄 Starting pipeline for: {filename}")
        
        # TODO: Implement actual pipeline
        # 1. AssemblyAI transcription
        # 2. LLM blog idea generation  
        # 3. Save to database
        
        # For now, just simulate processing
        print(f"🎙️ [PLACEHOLDER] Transcribing audio...")
        time.sleep(1)
        print(f"🤖 [PLACEHOLDER] Generating blog ideas...")
        time.sleep(1)
        print(f"💾 [PLACEHOLDER] Saving to database...")
        print(f"✅ Pipeline completed for: {filename}")

def start_monitoring():
    """Start the file monitoring system"""
    print(f"👀 Starting file monitor...")
    print(f"📁 Watching folder: {WATCH_FOLDER}")
    print(f"🎯 Trigger pattern: {TRIGGER_PREFIX}*.{SUPPORTED_FORMATS}")
    print(f"📦 Temp folder: {TEMP_FOLDER}")
    print("🔄 Press Ctrl+C to stop")
    
    # Create event handler and observer
    event_handler = AudioFileHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
    
    # Start monitoring
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ Stopping file monitor...")
        observer.stop()
    
    observer.join()
    print("👋 File monitor stopped")

if __name__ == "__main__":
    start_monitoring()