from app import db, Job
from app import app

with app.app_context():
    # Drop the existing Job table
    Job.__table__.drop(db.engine)
    print("✅ Dropped Job table.")

    # Recreate all tables (including Job with BigInteger)
    db.create_all()
    print("✅ Recreated all tables with updated schema.")
