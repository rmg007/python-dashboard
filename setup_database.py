import sqlite3
import os
from datetime import datetime, timedelta
import random

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Connect to SQLite database (creates it if it doesn't exist)
conn = sqlite3.connect('data/app.db')
cursor = conn.cursor()

# Create permits table
cursor.execute('''
CREATE TABLE IF NOT EXISTS permits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    permit_number TEXT NOT NULL,
    description TEXT,
    valuation REAL,
    status TEXT,
    date_status DATE,
    action_by_dept TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

# Generate sample data if the table is empty
cursor.execute("SELECT COUNT(*) FROM permits")
if cursor.fetchone()[0] == 0:
    # Sample departments
    departments = ['Building', 'Planning', 'Fire', 'Public Works', 'Zoning']
    
    # Generate sample permits
    for i in range(1, 101):
        dept = random.choice(departments)
        cursor.execute('''
        INSERT INTO permits (permit_number, description, valuation, status, date_status, action_by_dept)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            f'PER-{2023}-{i:04d}',
            f'Sample Permit {i}',
            round(random.uniform(1000, 500000), 2),
            random.choice(['Issued', 'Pending', 'Approved', 'Denied']),
            (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
            dept
        ))

# Create vw_filters view
cursor.execute('''
CREATE VIEW IF NOT EXISTS vw_filters AS
SELECT DISTINCT 
    strftime('%Y', date_status) AS year,
    strftime('%m', date_status) AS month,
    action_by_dept
FROM permits
WHERE date_status IS NOT NULL;
''')

# Commit changes and close connection
conn.commit()
conn.close()

print("Database setup complete! Created 'permits' table and 'vw_filters' view with sample data.")
