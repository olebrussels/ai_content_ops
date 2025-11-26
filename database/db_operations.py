import sqlite3
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import (
    Conversation, ConversationCreate, 
    BlogPostIdea, BlogPostIdeaCreate,
    ProcessingStatus
)

# Database path points to /data folder
DATABASE_PATH = "data/app.db"

class DatabaseManager:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    # =================================
    # CONVERSATION OPERATIONS
    # =================================
    
    def create_conversation(self, conversation: ConversationCreate) -> int:
        """Insert new conversation and return ID"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (title, raw_text, source, word_count)
                VALUES (?, ?, ?, ?)
            """, (
                conversation.title, 
                conversation.raw_text, 
                conversation.source,
                conversation.word_count
            ))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """Get conversation by ID"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,))
            row = cursor.fetchone()
            if row:
                return Conversation(**dict(row))
            return None
        finally:
            conn.close()
    
    def get_all_conversations(self) -> List[Conversation]:
        """Get all conversations ordered by newest first"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM conversations ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [Conversation(**dict(row)) for row in rows]
        finally:
            conn.close()
    
    def update_conversation_status(self, conversation_id: int, status: str):
        """Update conversation status"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE conversations SET status = ? WHERE id = ?",
                (status, conversation_id)
            )
            conn.commit()
        finally:
            conn.close()
    
    # =================================
    # BLOG POST IDEA OPERATIONS
    # =================================
    
    def create_blog_post_idea(self, idea: BlogPostIdeaCreate) -> int:
        """Insert blog post idea and return ID"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Calculate total_score (not in the model, computed here)
            total_score = (
                idea.usefulness_potential +
                idea.fitwith_seo_strategy +
                idea.fitwith_content_strategy +
                idea.inspiration_potential +
                idea.collaboration_potential +
                idea.innovation +
                idea.difficulty
            )
            
            # INSERT with 13 columns (12 from model + 1 calculated)
            cursor.execute("""
                INSERT INTO blog_post_ideas 
                (conversation_id, title, description, 
                 usefulness_potential, fitwith_seo_strategy, fitwith_content_strategy,
                 inspiration_potential, collaboration_potential, innovation, difficulty,
                 total_score, sent_to_prod, raw_llm_response)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                idea.conversation_id,           # 1
                idea.title,                     # 2
                idea.description,               # 3
                idea.usefulness_potential,      # 4
                idea.fitwith_seo_strategy,      # 5
                idea.fitwith_content_strategy,  # 6
                idea.inspiration_potential,     # 7
                idea.collaboration_potential,   # 8
                idea.innovation,                # 9
                idea.difficulty,                # 10
                total_score,                    # 11 (CALCULATED)
                idea.sent_to_prod,              # 12
                idea.raw_llm_response           # 13
            ))
            
            conn.commit()
            return cursor.lastrowid
            
        finally:
            conn.close()
    
    def get_ideas_by_conversation(self, conversation_id: int) -> List[BlogPostIdea]:
        """Get all blog post ideas for a conversation"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM blog_post_ideas WHERE conversation_id = ? ORDER BY total_score DESC",
                (conversation_id,)
            )
            rows = cursor.fetchall()
            return [BlogPostIdea(**dict(row)) for row in rows]
        finally:
            conn.close()
    
    def get_all_ideas(self, limit: int = 50) -> List[BlogPostIdea]:
        """Get all blog post ideas ordered by highest score"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM blog_post_ideas ORDER BY total_score DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [BlogPostIdea(**dict(row)) for row in rows]
        finally:
            conn.close()
    
    def get_idea(self, idea_id: int) -> Optional[BlogPostIdea]:
        """Get single blog post idea by ID"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM blog_post_ideas WHERE id = ?", (idea_id,))
            row = cursor.fetchone()
            if row:
                return BlogPostIdea(**dict(row))
            return None
        finally:
            conn.close()
    
    def mark_idea_sent_to_prod(self, idea_id: int) -> bool:
        """Mark a blog post idea as sent to production"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE blog_post_ideas SET sent_to_prod = 1 WHERE id = ?",
                (idea_id,)
            )
            conn.commit()
            return cursor.rowcount > 0  # Return True if a row was updated
        finally:
            conn.close()
    
    def get_pending_ideas(self, limit: int = 20) -> List[BlogPostIdea]:
        """Get blog post ideas not yet sent to production"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM blog_post_ideas WHERE sent_to_prod = 0 ORDER BY total_score DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [BlogPostIdea(**dict(row)) for row in rows]
        finally:
            conn.close()
    
    # =================================
    # COMBINED QUERIES
    # =================================
    
    def get_conversation_with_ideas(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        """Get conversation and all its ideas together"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        ideas = self.get_ideas_by_conversation(conversation_id)
        
        return {
            "conversation": conversation,
            "ideas": ideas,
            "idea_count": len(ideas),
            "best_score": max([idea.total_score for idea in ideas], default=0)
        }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get overview data for dashboard"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Count conversations
            cursor.execute("SELECT COUNT(*) FROM conversations")
            conversation_count = cursor.fetchone()[0]
            
            # Count ideas
            cursor.execute("SELECT COUNT(*) FROM blog_post_ideas")
            idea_count = cursor.fetchone()[0]
            
            # Get top ideas
            cursor.execute("""
                SELECT * FROM blog_post_ideas 
                ORDER BY total_score DESC 
                LIMIT 10
            """)
            top_ideas = [BlogPostIdea(**dict(row)) for row in cursor.fetchall()]
            
            return {
                "conversation_count": conversation_count,
                "idea_count": idea_count,
                "top_ideas": top_ideas
            }
        finally:
            conn.close()


# Global instance
db = DatabaseManager()