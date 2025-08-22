# 📊 Wellness Monitoring Dashboard  
*Emotion-aware dashboard combining AI, MySQL, and Power BI for employee wellness analytics.*

---

## 🌟 Overview  
The **Wellness Monitoring Dashboard** is a data-driven system that combines **facial emotion recognition, survey data, and session tracking** to analyze employee wellness. It integrates **Python, MySQL, and Power BI** to generate real-time and historical insights, empowering organizations to improve workplace well-being.

---

## 🔑 Features  
- 🎭 **Emotion Recognition** – Detects emotions (happy, sad, angry, fear, neutral, etc.) using OpenCV.  
- 🗄 **Centralized Database** – MySQL stores sessions, surveys, and daily metrics.  
- 📈 **Interactive Dashboard** – Power BI visualizes employee wellness trends.  
- 🔄 **Automated Refresh** – Dashboards reflect updated data from the database.  
- ⚡ **Scalable Design** – Easily extendable to new wellness parameters or HR systems.  

---

## 🛠 Tech Stack  
- **Python** – OpenCV, pandas, NumPy, SQLAlchemy  
- **Database** – MySQL  
- **Visualization** – Power BI  

---

## 📂 Database Schema  
- **employees** – Employee details (ID, alias, role, team).  
- **sessions** – Session logs with device IDs and timestamps.  
- **face_events** – Emotion recognition data for each session.  
- **pulse_survey** – Feedback from wellness surveys.  
- **daily_metrices** – Aggregated wellness data.  

---

## ⚙️ Installation & Setup  

1. **Clone the repo**  
   ```bash
   git clone https://github.com/your-username/wellness-dashboard.git
   cd wellness-dashboard

  2. Set up MySQL Database

Import schema from /db/schema.sql.

Update credentials in config.py.

3. Install Python dependencies

pip install -r requirements.txt

4. Run data pipeline

python aggregate_daily.py

5. Connect Power BI

Use localhost:3306 MySQL as data source.

Select related tables and build your dashboard.
