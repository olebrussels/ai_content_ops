import os
import glob
from pathlib import Path
from database.db_operations import db
from database.models import ConversationCreate, BlogPostIdeaCreate

# Configuration
TEMP_FOLDER = "data/temp"
SUPPORTED_FORMATS = ['.wav', '.mp3', '.m4a']

def find_audio_files():
    """Find all audio files in temp folder"""
    audio_files = []
    
    for format_ext in SUPPORTED_FORMATS:
        pattern = os.path.join(TEMP_FOLDER, f"*{format_ext}")
        files = glob.glob(pattern)
        audio_files.extend(files)
    
    return sorted(audio_files)

def process_single_file(file_path):
    """Process a single audio file"""
    filename = os.path.basename(file_path)
    print(f"\n🎵 Processing: {filename}")
    print(f"📁 File path: {file_path}")
    print(f"📊 File size: {os.path.getsize(file_path)} bytes")
    
    try:
        # Step 1: Transcribe with AssemblyAI (placeholder)
        print("🎙️ [PLACEHOLDER] Transcribing with AssemblyAI...")
        transcript_text = f"This is a placeholder transcript for {filename}. In real implementation, this would be the actual transcribed text from AssemblyAI."
        
        # Step 2: Save conversation to database
        print("💾 Saving conversation to database...")
        conversation = ConversationCreate(
            title=f"Audio: {filename}",
            raw_text=transcript_text,
            source="transcribed"
        )
        conversation_id = db.create_conversation(conversation)
        print(f"✅ Saved conversation with ID: {conversation_id}")
        
        # Step 3: Generate blog ideas with LLM (placeholder)
        print("🤖 [PLACEHOLDER] Generating blog ideas with LLM...")
        
        # Create some mock blog ideas
        mock_ideas = [
            {
                "title": f"Key Insights from {filename.replace('.wav', '')}",
                "description": "Main takeaways and actionable insights from this conversation",
                "usefulness_potential": 8,
                "fitwith_seo_strategy": 7,
                "fitwith_content_strategy": 8,
                "inspiration_potential": 6,
                "collaboration_potential": 7,
                "innovation": 6,
                "difficulty": 5
            },
            {
                "title": f"Lessons Learned: {filename.replace('.wav', '')}",
                "description": "Strategic lessons and implementation ideas",
                "usefulness_potential": 7,
                "fitwith_seo_strategy": 6,
                "fitwith_content_strategy": 7,
                "inspiration_potential": 8,
                "collaboration_potential": 6,
                "innovation": 7,
                "difficulty": 6
            }
        ]
        
        # Step 4: Save blog ideas to database
        print("💡 Saving blog ideas to database...")
        for idea_data in mock_ideas:
            blog_idea = BlogPostIdeaCreate(
                conversation_id=conversation_id,
                sent_to_prod=False,  # NEW FIELD
                **idea_data,
                raw_llm_response="Mock LLM response"
            )
            idea_id = db.create_blog_post_idea(blog_idea)
            print(f"   ✅ Saved idea: '{idea_data['title']}' (ID: {idea_id}, Score: {blog_idea.total_score})")
        
        print(f"🎉 Successfully processed: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {filename}: {e}")
        return False

def process_all_files(delete_after_processing=False):
    """Process all audio files in temp folder"""
    print("🔍 Scanning for audio files...")
    
    # Ensure temp folder exists
    os.makedirs(TEMP_FOLDER, exist_ok=True)
    
    # Find all audio files
    audio_files = find_audio_files()
    
    if not audio_files:
        print(f"❌ No audio files found in {TEMP_FOLDER}")
        print(f"   Supported formats: {SUPPORTED_FORMATS}")
        return
    
    print(f"📊 Found {len(audio_files)} audio files:")
    for file_path in audio_files:
        filename = os.path.basename(file_path)
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        print(f"   📁 {filename} ({size_mb:.1f} MB)")
    
    # Ask for confirmation
    response = input(f"\n🤔 Process {len(audio_files)} files? (y/N): ").lower()
    if response not in ['y', 'yes']:
        print("⏹️ Processing cancelled")
        return
    
    # Process each file
    print("\n🚀 Starting batch processing...")
    processed_count = 0
    failed_count = 0
    
    for file_path in audio_files:
        success = process_single_file(file_path)
        
        if success:
            processed_count += 1
            if delete_after_processing:
                os.remove(file_path)
                print(f"🗑️ Deleted: {os.path.basename(file_path)}")
        else:
            failed_count += 1
    
    # Summary
    print(f"\n📊 Batch Processing Complete!")
    print(f"✅ Successfully processed: {processed_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📁 Total files: {len(audio_files)}")

def main():
    """Main function with menu"""
    print("🎙️ Manual Audio Processor")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. List audio files in temp folder")
        print("2. Process all files (keep files after processing)")
        print("3. Process all files (delete files after processing)")
        print("4. View recent database entries")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            audio_files = find_audio_files()
            if audio_files:
                print(f"\n📁 Files in {TEMP_FOLDER}:")
                for file_path in audio_files:
                    filename = os.path.basename(file_path)
                    size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    print(f"   {filename} ({size_mb:.1f} MB)")
            else:
                print(f"\n❌ No audio files found in {TEMP_FOLDER}")
        
        elif choice == "2":
            process_all_files(delete_after_processing=False)
        
        elif choice == "3":
            process_all_files(delete_after_processing=True)
        
        elif choice == "4":
            print("\n📊 Recent Database Entries:")
            conversations = db.get_all_conversations()
            for conv in conversations[:5]:  # Show last 5
                ideas = db.get_ideas_by_conversation(conv.id)
                print(f"   📝 {conv.title} ({len(ideas)} ideas)")
        
        elif choice == "5":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please select 1-5.")

if __name__ == "__main__":
    main()
