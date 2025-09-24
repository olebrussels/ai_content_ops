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
        print(f"📁 Temp folder ready: {TEMP_FOLDER}")
    
    def on_created(self, event):
        """Handle new file creation (usually Nextcloud temp files)"""
        if event.is_directory:
            return
        
        filename = os.path.basename(event.src_path)
        if self.is_nextcloud_temp_file(filename):
            print(f"⏳ Nextcloud syncing: {filename}")
    
    def on_moved(self, event):
        """Handle file moves (Nextcloud temp → final file)"""
        if os.path.isdir(event.dest_path):
            return
            
        filename = os.path.basename(event.dest_path)
        print(f"📥 File synced: {filename}")
        
        if self.should_process_file(filename):
            self.stage_audio_file(event.dest_path, filename)
    
    def is_nextcloud_temp_file(self, filename):
        """Check if this is a Nextcloud temporary file"""
        return (
            filename.startswith('.') or 
            '~' in filename or 
            filename.endswith('.tmp')
        )
    
    def should_process_file(self, filename):
        """Check if file should be staged for processing"""
        name_lower = filename.lower()
        
        # Must start with trigger prefix
        if not name_lower.startswith(TRIGGER_PREFIX):
            print(f"⏭️  Ignoring (no '{TRIGGER_PREFIX}' prefix): {filename}")
            return False
        
        # Must be supported audio format
        if not any(name_lower.endswith(ext) for ext in SUPPORTED_FORMATS):
            print(f"⏭️  Ignoring (unsupported format): {filename}")
            return False
        
        return True
    
    def stage_audio_file(self, source_path, filename):
        """Copy audio file to temp folder for processing"""
        try:
            print(f"🎵 Staging audio file: {filename}")
            
            # Copy to temp folder
            temp_path = os.path.join(TEMP_FOLDER, filename)
            
            # Check if file already exists in temp
            if os.path.exists(temp_path):
                print(f"⚠️  File already exists in temp, skipping: {filename}")
                return
            
            # Wait a moment for file to finish syncing
            time.sleep(2)
            
            # Copy file
            shutil.copy2(source_path, temp_path)
            print(f"✅ Staged to temp: {temp_path}")
            
            # Get file info
            size_mb = os.path.getsize(temp_path) / (1024 * 1024)
            print(f"📊 File size: {size_mb:.1f} MB")
            
            # Remove original from Talk folder (keep Nextcloud clean)
            os.remove(source_path)
            print(f"🗑️ Removed original from: {WATCH_FOLDER}")
            
            print(f"🎯 Ready for processing: {filename}")
            
        except Exception as e:
            print(f"❌ Error staging {filename}: {e}")

def start_monitoring():
    """Start the file monitoring system"""
    print("🎙️ Audio File Monitor")
    print("=" * 40)
    print(f"👀 Watching: {WATCH_FOLDER}")
    print(f"🎯 Trigger: {TRIGGER_PREFIX}*{SUPPORTED_FORMATS}")
    print(f"📦 Staging: {TEMP_FOLDER}")
    print(f"🔄 Press Ctrl+C to stop")
    print()
    
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

def list_staged_files():
    """Utility function to list files in temp folder"""
    import glob
    
    print(f"📁 Files staged in {TEMP_FOLDER}:")
    
    audio_files = []
    for ext in SUPPORTED_FORMATS:
        pattern = os.path.join(TEMP_FOLDER, f"*{ext}")
        audio_files.extend(glob.glob(pattern))
    
    if audio_files:
        for file_path in sorted(audio_files):
            filename = os.path.basename(file_path)
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"   🎵 {filename} ({size_mb:.1f} MB)")
        print(f"\n📊 Total: {len(audio_files)} files ready for processing")
    else:
        print("   (No audio files found)")
    
    return audio_files

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        # python file_monitor.py list
        list_staged_files()
    else:
        # python file_monitor.py (default: start monitoring)
        start_monitoring()

