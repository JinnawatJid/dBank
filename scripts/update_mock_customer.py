import os
import psycopg2

def simulate_historical_change():
    print("Simulating historical change for SCD Type 2 demonstration on CUST-00001...")

    db_name = os.getenv("POSTGRES_DB", "dbank_analytics")
    db_user = os.getenv("POSTGRES_USER", "dbank_admin")
    db_password = os.getenv("POSTGRES_PASSWORD", "secure_admin_password_here")
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

        cur.execute("""
            UPDATE raw.customers
            SET customer_segment = 'Wealth',
                _ingested_at = NOW()
            WHERE customer_id = 'CUST-00001';
        """)
        print("Successfully updated CUST-00001 to 'Wealth' segment.")

    except Exception as e:
        print(f"Error simulating historical change: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    simulate_historical_change()
