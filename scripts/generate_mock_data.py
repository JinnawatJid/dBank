import csv
import os
import random
from datetime import datetime, timedelta
from faker import Faker
import psycopg2

fake = Faker()

# Configuration
NUM_CUSTOMERS = 1000
NUM_PRODUCTS = 10
NUM_TICKETS = 5000
NUM_LOGINS = 10000

DATA_DIR = "data/raw"
os.makedirs(DATA_DIR, exist_ok=True)

# Define schemas and file paths
CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.csv")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.csv")
TICKETS_FILE = os.path.join(DATA_DIR, "tickets.csv")
LOGINS_FILE = os.path.join(DATA_DIR, "logins.csv")

def generate_customers():
    print(f"Generating {NUM_CUSTOMERS} customers...")
    segments = ['Retail', 'Wealth', 'Corporate']
    with open(CUSTOMERS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['customer_id', 'first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'join_date', 'customer_segment'])
        for i in range(1, NUM_CUSTOMERS + 1):
            writer.writerow([
                f"CUST-{i:05d}",
                fake.first_name(),
                fake.last_name(),
                fake.email(),
                fake.phone_number(),
                fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat(),
                fake.date_between(start_date='-5y', end_date='today').isoformat(),
                random.choice(segments)
            ])

def generate_products():
    print(f"Generating {NUM_PRODUCTS} products...")
    product_types = ['Checking Account', 'Savings Account', 'Credit Card', 'Loan', 'Investment']
    with open(PRODUCTS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['product_id', 'product_name', 'product_type', 'launch_date'])
        for i in range(1, NUM_PRODUCTS + 1):
            ptype = random.choice(product_types)
            writer.writerow([
                f"PROD-{i:03d}",
                f"{fake.company()} {ptype}",
                ptype,
                fake.date_between(start_date='-10y', end_date='-1y').isoformat()
            ])

def generate_tickets():
    print(f"Generating {NUM_TICKETS} tickets...")
    issue_types = ['Login Issue', 'Transaction Dispute', 'Card Replacement', 'Account Inquiry', 'Fee Dispute']
    statuses = ['Open', 'In Progress', 'Resolved', 'Closed']
    priorities = ['Low', 'Medium', 'High', 'Critical']
    with open(TICKETS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ticket_id', 'customer_id', 'product_id', 'issue_type', 'status', 'priority', 'created_at', 'resolved_at'])
        for i in range(1, NUM_TICKETS + 1):
            import datetime
            created_at = fake.date_time_between(start_date='-1y', end_date='now', tzinfo=datetime.timezone.utc)
            status = random.choices(statuses, weights=[0.1, 0.1, 0.3, 0.5])[0]
            resolved_at = ''
            if status in ['Resolved', 'Closed']:
                resolved_at = (created_at + timedelta(days=random.randint(1, 14))).isoformat()

            writer.writerow([
                f"TKT-{i:06d}",
                f"CUST-{random.randint(1, NUM_CUSTOMERS):05d}",
                f"PROD-{random.randint(1, NUM_PRODUCTS):03d}",
                random.choice(issue_types),
                status,
                random.choice(priorities),
                created_at.isoformat(),
                resolved_at
            ])

def generate_logins():
    print(f"Generating {NUM_LOGINS} logins...")
    statuses = ['Success', 'Failed']
    device_types = ['Mobile App', 'Web Browser', 'Tablet']
    with open(LOGINS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['login_id', 'customer_id', 'login_timestamp', 'ip_address', 'device_type', 'status'])
        for i in range(1, NUM_LOGINS + 1):
            import datetime
            writer.writerow([
                f"LOG-{i:07d}",
                f"CUST-{random.randint(1, NUM_CUSTOMERS):05d}",
                fake.date_time_between(start_date='-1y', end_date='now', tzinfo=datetime.timezone.utc).isoformat(),
                fake.ipv4(),
                random.choice(device_types),
                random.choices(statuses, weights=[0.9, 0.1])[0]
            ])

def load_data_to_db():
    print("Loading data into PostgreSQL...")
    # Read from environment variables, fallback to defaults
    db_name = os.getenv("POSTGRES_DB", "dbank_analytics")
    db_user = os.getenv("POSTGRES_USER", "dbank_admin")
    db_password = os.getenv("POSTGRES_PASSWORD", "secure_admin_password_here")

    # We use localhost since we are running postgres locally in the sandbox
    db_host = "127.0.0.1"
    db_port = os.getenv("POSTGRES_PORT", "5432")

    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Create schema
        cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")

        # Create tables
        cur.execute("""
            DROP TABLE IF EXISTS raw.customers CASCADE;
            CREATE TABLE raw.customers (
                customer_id VARCHAR(50) PRIMARY KEY,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                email VARCHAR(255),
                phone VARCHAR(50),
                date_of_birth DATE,
                join_date DATE,
                customer_segment VARCHAR(50),
                _ingested_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        cur.execute("""
            DROP TABLE IF EXISTS raw.products CASCADE;
            CREATE TABLE raw.products (
                product_id VARCHAR(50) PRIMARY KEY,
                product_name VARCHAR(255),
                product_type VARCHAR(100),
                launch_date DATE,
                _ingested_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        cur.execute("""
            DROP TABLE IF EXISTS raw.tickets CASCADE;
            CREATE TABLE raw.tickets (
                ticket_id VARCHAR(50) PRIMARY KEY,
                customer_id VARCHAR(50),
                product_id VARCHAR(50),
                issue_type VARCHAR(100),
                status VARCHAR(50),
                priority VARCHAR(50),
                created_at TIMESTAMPTZ,
                resolved_at TIMESTAMPTZ,
                _ingested_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        cur.execute("""
            DROP TABLE IF EXISTS raw.logins CASCADE;
            CREATE TABLE raw.logins (
                login_id VARCHAR(50) PRIMARY KEY,
                customer_id VARCHAR(50),
                login_timestamp TIMESTAMPTZ,
                ip_address VARCHAR(50),
                device_type VARCHAR(50),
                status VARCHAR(50),
                _ingested_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        # Load data using COPY
        files_to_load = [
            (CUSTOMERS_FILE, 'raw.customers'),
            (PRODUCTS_FILE, 'raw.products'),
            (TICKETS_FILE, 'raw.tickets'),
            (LOGINS_FILE, 'raw.logins'),
        ]

        for filepath, table in files_to_load:
            print(f"Loading {filepath} into {table}...")
            # We need to specify the columns we are loading into because we added _ingested_at
            # to the schema, but it is not in the CSV files.
            # First, read the header from the CSV file to get the column names.
            with open(filepath, 'r') as f:
                header = f.readline().strip()
                columns = header.split(',')
                # rewind the file
                f.seek(0)
                # Use COPY expert to handle CSV with header
                cur.copy_expert(f"COPY {table} ({','.join(columns)}) FROM STDIN WITH (FORMAT CSV, HEADER)", f)

        print("Data loaded successfully.")

        # Grant least privilege access to the read-only user
        try:
            readonly_user = os.getenv("READONLY_USER", "dbank_readonly")

            # Check if user exists before attempting grants
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (readonly_user,))
            if cur.fetchone():
                print(f"Granting read-only access to user {readonly_user}...")
                cur.execute(f"GRANT USAGE ON SCHEMA raw TO {readonly_user};")
                cur.execute(f"GRANT SELECT ON ALL TABLES IN SCHEMA raw TO {readonly_user};")
                # Also ensure future tables get these permissions (though not strictly necessary for this static setup)
                cur.execute(f"ALTER DEFAULT PRIVILEGES IN SCHEMA raw GRANT SELECT ON TABLES TO {readonly_user};")
                print("Permissions granted.")
            else:
                print(f"Warning: User {readonly_user} not found. Skipping permission grants.")
        except Exception as perm_error:
            print(f"Warning: Could not grant permissions: {perm_error}")

        # Verify
        cur.execute("SELECT count(*) FROM raw.customers;")
        print(f"Customers loaded: {cur.fetchone()[0]}")

    except Exception as e:
        print(f"Error loading data: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    generate_customers()
    generate_products()
    generate_tickets()
    generate_logins()
    load_data_to_db()
