🚀 Job Market Trends
An end-to-end Job Market Trends Analysis and Search Platform leveraging PySpark for batch processing and a Flask web interface to explore, search, and save jobs efficiently.

📌 Project Overview
This project allows users to:
✅ Search for jobs by title, location, and skills
✅ Save jobs for later viewing
✅ Sign up and log in with OTP verification (using Twilio + pyotp) for secure access
✅ View categorized insights for remote, onsite, experience-based jobs
✅ Use a clean Flask-based dashboard for a seamless experience

Spark is used for batch processing and dataset preparation, ensuring cleaned and structured data for the Flask app.

🗂️ Dataset Sources
Used real-world Kaggle job market datasets:

1️⃣ LinkedIn Job Postings
2️⃣ LinkedIn Data Science Jobs Pakistan July 2024

Processed using PySpark for:

Null handling

Date consistency

Deduplication

Field standardization

⚙️ Tech Stack
Python 3.11

Apache Spark (PySpark) – batch processing and data cleaning

Flask – backend framework

Flask-SQLAlchemy – user and saved job management

SQLite – lightweight database for user management and saved jobs

PyOTP + Twilio – OTP-based user verification

Matplotlib, Pandas – for data manipulation and plotting if required

HTML, CSS, Jinja2 – frontend templating

🚀 Features
✅ User Authentication with OTP Verification:
Secure sign-up/login using Twilio + PyOTP for OTP-based verification.

✅ Search and Save Jobs:
Search jobs by title, location, or skill and save interesting jobs for later.

✅ Clean, Categorized Data:
Separate views for remote, onsite, and experience-level jobs.

✅ Responsive Dashboard:
Includes user dashboard, search view, saved jobs view, and service information.

✅ PySpark Batch Processing Pipeline:
Automates dataset cleaning and transformation for scalable, consistent data.

🛠️ Setup Instructions

1️⃣ Clone the Repository
git clone https://github.com/yourusername/job-market-trends.git
cd job-market-trends

2️⃣ Create and Activate Virtual Environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3️⃣ Install Requirements
pip install -r requirements.txt

4️⃣ Download and Place Datasets

5️⃣ Run the Flask Application
http://127.0.0.1:5000 to use the Job Market Trends Analyzer.

🖥️ Pages Included

✅ Landing Page (index.html) – Introduction to the platform

✅ Login and Signup (login.html, signup.html) – Secure authentication

✅ Dashboard (dashboard.html) – User overview and navigation

✅ Search Jobs (search_jobs.html) – Search and explore available jobs

✅ Saved Jobs (saved_jobs.html) – Review saved jobs

✅ Services (services.html) – Project and feature details

🔮 Future Enhancements
Deploy on Heroku or AWS EC2 for public access

Add admin analytics dashboard for top locations/skills

Include email notifications for saved jobs

Integrate real-time streaming using Spark Structured Streaming

🛡️ License
MIT License – Free for academic use and personal portfolio projects.

✨ Credits
Developed by Muhammad Bilal
For questions or collaboration: 
www.linkedin.com/in/bilal-iftikhar-26130a262 or bilaliftikhar.967@gmail.com.
