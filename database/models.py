from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# =================================
# CONVERSATION MODELS
# =================================

class ConversationCreate(BaseModel):
    """Model for creating a new conversation"""
    title: Optional[str] = None
    raw_text: str = Field(min_length=10, description="The conversation text content")
    source: str = Field(default='manual', description="Source: manual, transcribed, imported")
    
    @property
    def word_count(self) -> int:
        """Calculate word count from raw text"""
        return len(self.raw_text.split())

class Conversation(BaseModel):
    """Model for reading conversation from database"""
    id: int
    title: Optional[str]
    raw_text: str
    source: str
    word_count: int
    created_at: datetime
    status: str

# =================================
# BLOG POST IDEA MODELS
# =================================

class BlogPostIdeaStructure(BaseModel):
    """Model for LLM to generate structured blog post ideas"""
    title: str = Field(description="The name of the idea for writing a blog post")
    description: str = Field(description="Brief description of the blog post")
    usefulness_potential: int = Field(ge=1, le=10, description="How useful this post will be to the reader")
    fitwith_seo_strategy: int = Field(ge=1, le=10, description="How this post fits with company SEO strategy")
    fitwith_content_strategy: int = Field(ge=1, le=10, description="How this post fits with company content strategy")
    inspiration_potential: int = Field(ge=1, le=10, description="How can this post inspire readers to act")
    collaboration_potential: int = Field(ge=1, le=10, description="How this post incite others to collaborate")
    innovation: int = Field(ge=1, le=10, description="Uniqueness score (10 = very unique)")
    difficulty: int = Field(ge=1, le=10, description="Complexity to write (1 = easy, 10 = complex)")

class BlogPostIdeaCreate(BaseModel):
    """Model for creating a new blog post idea"""
    conversation_id: int
    title: str
    description: str
    usefulness_potential: int
    fitwith_seo_strategy: int
    fitwith_content_strategy: int
    inspiration_potential: int
    collaboration_potential: int
    innovation: int
    difficulty: int
    raw_llm_response: Optional[str] = None
    
    @property
    def total_score(self) -> int:
        """Calculate total score for the idea"""
        return (
            self.usefulness_potential +
            self.fitwith_seo_strategy +
            self.fitwith_content_strategy +
            self.inspiration_potential +
            self.collaboration_potential +
            self.innovation +
            (11 - self.difficulty)  # Invert difficulty (easier = better score)
        )

class BlogPostIdea(BaseModel):
    """Model for reading blog post idea from database"""
    id: int
    conversation_id: int
    title: str
    description: str
    usefulness_potential: int
    fitwith_seo_strategy: int
    fitwith_content_strategy: int
    inspiration_potential: int
    collaboration_potential: int
    innovation: int
    difficulty: int
    total_score: int
    raw_llm_response: Optional[str]
    created_at: datetime

# =================================
# HELPER MODELS
# =================================

class ProcessingStatus(BaseModel):
    """Model for tracking processing status"""
    id: int
    conversation_id: int
    stage: str
    status: str
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]