from database.init_db import create_database, reset_database
from database.db_operations import db
from database.models import ConversationCreate, BlogPostIdeaCreate

def test_database_complete():
    """Complete test of database functionality"""
    print("🧪 Starting complete database test...\n")
    
    # Step 1: Reset database
    print("1. Resetting database...")
    reset_database()
    
    # Step 2: Create a test conversation
    print("2. Creating test conversation...")
    test_conversation = ConversationCreate(
        title="Meeting with Client about AI Strategy",
        raw_text="""
        We discussed implementing AI in their marketing workflow. 
        The client is interested in automated content generation and 
        personalized email campaigns. They have budget constraints but 
        see the potential ROI. Main concerns are data privacy and 
        integration with existing systems.
        """,
        source="manual"
    )
    
    conversation_id = db.create_conversation(test_conversation)
    print(f"✅ Created conversation with ID: {conversation_id}")
    
    # Step 3: Retrieve the conversation
    print("3. Retrieving conversation...")
    conversation = db.get_conversation(conversation_id)
    print(f"✅ Retrieved: '{conversation.title}' ({conversation.word_count} words)")
    
    # Step 4: Create test blog post ideas
    print("4. Creating test blog post ideas...")
    
    ideas_data = [
        {
            "title": "AI Marketing Automation for Small Businesses",
            "description": "A guide on implementing AI marketing tools within budget constraints",
            "usefulness_potential": 9,
            "fitwith_seo_strategy": 8,
            "fitwith_content_strategy": 9,
            "inspiration_potential": 7,
            "collaboration_potential": 6,
            "innovation": 7,
            "difficulty": 5
        },
        {
            "title": "Data Privacy in AI Marketing: What Clients Need to Know",
            "description": "Addressing privacy concerns when implementing AI marketing solutions",
            "usefulness_potential": 8,
            "fitwith_seo_strategy": 9,
            "fitwith_content_strategy": 8,
            "inspiration_potential": 6,
            "collaboration_potential": 8,
            "innovation": 6,
            "difficulty": 6
        },
        {
            "title": "ROI Calculator: AI Marketing Tools vs Traditional Methods",
            "description": "Interactive tool to help businesses calculate AI marketing ROI",
            "usefulness_potential": 10,
            "fitwith_seo_strategy": 7,
            "fitwith_content_strategy": 8,
            "inspiration_potential": 8,
            "collaboration_potential": 9,
            "innovation": 9,
            "difficulty": 8
        }
    ]
    
    idea_ids = []
    for idea_data in ideas_data:
        idea = BlogPostIdeaCreate(
            conversation_id=conversation_id,
            **idea_data,
            raw_llm_response="Test LLM response"
        )
        idea_id = db.create_blog_post_idea(idea)
        idea_ids.append(idea_id)
        print(f"✅ Created idea: '{idea.title}' (Score: {idea.total_score})")
    
    # Step 5: Test retrieval functions
    print("\n5. Testing retrieval functions...")
    
    # Get ideas by conversation
    ideas = db.get_ideas_by_conversation(conversation_id)
    print(f"✅ Found {len(ideas)} ideas for conversation {conversation_id}")
    
    # Get all ideas
    all_ideas = db.get_all_ideas()
    print(f"✅ Found {len(all_ideas)} total ideas")
    
    # Get conversation with ideas
    conv_with_ideas = db.get_conversation_with_ideas(conversation_id)
    print(f"✅ Conversation has {conv_with_ideas['idea_count']} ideas, best score: {conv_with_ideas['best_score']}")
    
    # Get dashboard data
    dashboard = db.get_dashboard_data()
    print(f"✅ Dashboard: {dashboard['conversation_count']} conversations, {dashboard['idea_count']} ideas")
    
    # Step 6: Display results
    print("\n6. Results Summary:")
    print("=" * 50)
    print(f"📝 Conversation: {conversation.title}")
    print(f"📊 Word count: {conversation.word_count}")
    print(f"💡 Generated ideas: {len(ideas)}")
    print("\n🏆 Top Ideas (by score):")
    
    for i, idea in enumerate(sorted(ideas, key=lambda x: x.total_score, reverse=True), 1):
        print(f"{i}. {idea.title} (Score: {idea.total_score})")
        print(f"   📝 {idea.description}")
        print(f"   🎯 Usefulness: {idea.usefulness_potential}/10, Difficulty: {idea.difficulty}/10")
        print()
    
    print("🎉 Database test completed successfully!")
    print(f"📁 Database file created at: data/app.db")

if __name__ == "__main__":
    test_database_complete()