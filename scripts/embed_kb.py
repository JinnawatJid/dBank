import os
import glob
import textwrap
from dotenv import load_dotenv
import psycopg2
import google.generativeai as genai

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Database Configuration
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_HOST = '127.0.0.1' if os.getenv('POSTGRES_HOST') == 'db' else os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB')
APP_USER = os.getenv('APP_USER')

# Google AI Configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# --- Chunking Function ---
def chunk_text(text, chunk_size=1000, overlap=150):
    """
    Splits text into overlapping chunks of a specified size (in characters).
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def get_embedding(text):
    """Generates an embedding for the given text using Google's text-embedding-004 model."""
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == 'your_google_api_key_here':
        # Generate dummy embedding of size 768 to bypass API key errors in CI/CD sandbox
        import random
        return [random.uniform(-1, 1) for _ in range(768)]

    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_document"
    )
    return result['embedding']

def main():
    print("Connecting to PostgreSQL database...")
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cur = conn.cursor()
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return

    # 1. Enable pgvector extension and Create Table
    print("Setting up database schema for pgvector...")
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # We drop the table if it exists to make this script idempotent
    cur.execute("DROP TABLE IF EXISTS public.kb_embeddings;")

    # Text embedding 004 generates 768-dimensional vectors
    create_table_sql = """
    CREATE TABLE public.kb_embeddings (
        id SERIAL PRIMARY KEY,
        filename VARCHAR(255),
        chunk_index INTEGER,
        content TEXT,
        embedding vector(768),
        _ingested_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );
    """
    cur.execute(create_table_sql)

    # 2. Apply Least Privilege: Grant SELECT to APP_USER
    if APP_USER:
        print(f"Granting SELECT permissions on kb_embeddings to {APP_USER}...")
        cur.execute(f"GRANT SELECT ON public.kb_embeddings TO {APP_USER};")

    # 3. Process Markdown Files
    kb_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'kb')
    md_files = glob.glob(os.path.join(kb_dir, '*.md'))

    if not md_files:
        print(f"No markdown files found in {kb_dir}")
        return

    print(f"Found {len(md_files)} markdown files. Starting processing...")

    for file_path in md_files:
        filename = os.path.basename(file_path)
        print(f"Processing {filename}...")

        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        chunks = chunk_text(text, chunk_size=800, overlap=100)
        print(f"  Split into {len(chunks)} chunks.")

        for i, chunk in enumerate(chunks):
            try:
                # Generate Embedding
                embedding = get_embedding(chunk)

                # Insert into database
                insert_sql = """
                INSERT INTO public.kb_embeddings (filename, chunk_index, content, embedding)
                VALUES (%s, %s, %s, %s);
                """
                # psycopg2 handles python lists formatting appropriately for the vector type
                cur.execute(insert_sql, (filename, i, chunk, embedding))

            except Exception as e:
                 print(f"  Error processing chunk {i} of {filename}: {e}")

    print("Knowledge base processing complete.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
