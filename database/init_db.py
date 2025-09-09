import sqlite3
import os
from pathlib import Path

# Database goes in /data folder (not version controlled)
DATABASE_PATH = "data/app.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

def create_database():
    """Initialize SQLite database with schema"""
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    print(f"Creating database at: {DATABASE_PATH}")
    
    # Create database connection
    conn = sqlite3.connect(DATABASE_PATH)
    
    try:
        # Read schema file
        with open(SCHEMA_PATH, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema
        conn.executescript(schema_sql)
        print("✅ Database schema created successfully!")
        
        # Verify tables were created
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"✅ Created tables: {[table[0] for table in tables]}")
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        raise
    finally:
        conn.close()

def reset_database():
    """Delete and recreate database (useful for development)"""
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
        print("🗑️ Deleted existing database")
    create_database()

if __name__ == "__main__":
    create_database()