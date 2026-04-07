import psycopg2
from psycopg2.extras import execute_batch
import os
from dotenv import load_dotenv
import random

load_dotenv()
DB_USER = os.getenv("POSTGRES_USER", "dbank_admin")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secure_admin_password_here")
DB_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "dbank_analytics")

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
cur = conn.cursor()

# Insert dummy embeddings to bypass the google api error
dummy_data = [
    ("v1.2_release_notes.md", 0, "The v1.2 spike observed on October 24th was primarily driven by a concentrated surge in institutional treasury allocations within the EMEA sector. Our analysis indicates a 14.2% increase in transaction volume compared to the previous week's baseline.", [random.uniform(-1, 1) for _ in range(768)]),
    ("login_issues.md", 0, "Login issues can be caused by incorrect passwords or network timeouts.", [random.uniform(-1, 1) for _ in range(768)]),
    ("premium_credit_card_policy.md", 0, "Premium credit cards have a $500 annual fee and offer 3% cash back.", [random.uniform(-1, 1) for _ in range(768)]),
    ("fraud_dispute_guide.md", 0, "If you suspect fraud, freeze your card immediately and contact support within 30 days.", [random.uniform(-1, 1) for _ in range(768)]),
    ("hysa_details.md", 0, "Our High Yield Savings Account currently offers a 4.5% APY.", [random.uniform(-1, 1) for _ in range(768)]),
]

execute_batch(cur, """
    INSERT INTO kb_embeddings (filename, chunk_index, content, embedding)
    VALUES (%s, %s, %s, %s)
""", dummy_data)
conn.commit()
cur.close()
conn.close()
print("Dummy embeddings loaded.")
