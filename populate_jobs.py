import pyodbc
from app import app, db
from app import Job
from dotenv import load_dotenv
import os

load_dotenv()

server = os.getenv('AZURE_SERVER')
database = os.getenv('AZURE_DATABASE')
username = os.getenv('AZURE_USERNAME')
password = os.getenv('AZURE_PASSWORD')
driver = os.getenv('AZURE_DRIVER')

azure_conn_str = f"""
DRIVER={driver};
SERVER={server};
DATABASE={database};
UID={username};
PWD={password};
Encrypt=yes;
TrustServerCertificate=no;
Connection Timeout=30;
"""


# Azure SQL query to fetch jobs
query = """
SELECT job_id, company_name, title, description, location,
       remote_allowed, experience_level, skills_desc, listed_time
FROM JobMarketData
"""

def fetch_and_populate_jobs():
    print("⏳ Connecting to Azure SQL and fetching data...")

    with pyodbc.connect(azure_conn_str) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        print(f"📦 Fetched {len(rows)} jobs from Azure SQL.")

        with app.app_context():
            # Step 1: Clear all existing jobs (optional)
            print("🧹 Clearing existing job entries...")
            db.session.query(Job).delete()
            db.session.commit()

            # Step 2: Prepare Job objects
            print("⚙️ Creating job objects for bulk insert...")

            job_objects = []
            for row in rows:
                job = Job(
                    job_id=row.job_id,
                    company_name=row.company_name,
                    title=row.title,
                    location=row.location,
                    remote_allowed=bool(row.remote_allowed),
                    experience_level=row.experience_level,
                    skills_desc=row.skills_desc
                )
                job_objects.append(job)

            # Step 3: Fast bulk insert
            print("🚀 Inserting into SQLite using bulk_save_objects...")
            db.session.bulk_save_objects(job_objects)
            db.session.commit()

            print(f"✅ Successfully inserted {len(job_objects)} jobs into local DB.")

if __name__ == "__main__":
    fetch_and_populate_jobs()
