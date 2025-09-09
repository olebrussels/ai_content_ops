-- Conversations table: stores the raw text input
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    raw_text TEXT NOT NULL,
    source TEXT DEFAULT 'manual',
    word_count INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'processing', 'completed', 'error'))
);

-- Blog post ideas: generated directly from conversations
CREATE TABLE IF NOT EXISTS blog_post_ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    
    -- Scoring metrics (1-10 scale)
    usefulness_potential INTEGER CHECK(usefulness_potential BETWEEN 1 AND 10),
    fitwith_seo_strategy INTEGER CHECK(fitwith_seo_strategy BETWEEN 1 AND 10),
    fitwith_content_strategy INTEGER CHECK(fitwith_content_strategy BETWEEN 1 AND 10),
    inspiration_potential INTEGER CHECK(inspiration_potential BETWEEN 1 AND 10),
    collaboration_potential INTEGER CHECK(collaboration_potential BETWEEN 1 AND 10),
    innovation INTEGER CHECK(innovation BETWEEN 1 AND 10),
    difficulty INTEGER CHECK(difficulty BETWEEN 1 AND 10),
    
    -- Computed metrics
    total_score INTEGER,
    
    -- Optional: Store raw LLM output for debugging
    raw_llm_response TEXT,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- Processing status table: tracks async operations  
CREATE TABLE IF NOT EXISTS processing_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    stage TEXT NOT NULL, -- 'idea_generation', 'completed'
    status TEXT NOT NULL, -- 'pending', 'in_progress', 'completed', 'failed'
    error_message TEXT,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);