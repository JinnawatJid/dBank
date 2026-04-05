#!/bin/bash
set -e

echo "=== Running Data Generation & SCD Type 2 Demo Workflow ==="

echo "1. Generating mock data and loading into database..."
python scripts/generate_mock_data.py

echo "1.5 Installing dbt dependencies and building staging models..."
cd data/dbank_analytics
dbt deps
dbt run -s stg_customers
cd ../../

echo "2. Taking initial dbt snapshot..."
cd data/dbank_analytics
dbt snapshot
cd ../../

echo "3. Simulating a historical customer change..."
# Add a small delay to ensure the timestamp is different
sleep 2
python scripts/update_mock_customer.py

echo "4. Taking updated dbt snapshot..."
cd data/dbank_analytics
dbt snapshot
cd ../../

echo "5. Running all dbt models..."
cd data/dbank_analytics
dbt run
cd ../../

echo "=== Workflow Complete ==="
echo "You can now query dim_customers to see the history for CUST-00001!"
