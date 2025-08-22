import pandas as pd
import mysql.connector as mys
from sqlalchemy import create_engine

# -----------------------
# DB connection functions
# -----------------------
def get_conn():
    return mys.connect(
        host="localhost",
        user="root",
        password="1234",
        database="wellness_db"
    )

def get_engine():
    return create_engine("mysql+mysqlconnector://root:1234@localhost/wellness_db")

# -----------------------
# Main computation
# -----------------------
def compute_daily_metrices():
    # Use SQLAlchemy engine for pandas
    engine = get_engine()
    query = """
        SELECT s.employees_id, fe.ts, fe.dominant_emotion,
               fe.happy, fe.sad, fe.angry, fe.fear,
               fe.disgust, fe.surprise, fe.neutral
        FROM face_events fe
        JOIN sessions s ON fe.session_id = s.session_id
    """
    df = pd.read_sql(query, engine, parse_dates=['ts'])

    if df.empty:
        print("No face events yet.")
        return
    
    # Add date column
    df['date'] = df['ts'].dt.date
    emo_cols = ["happy", "sad", "angry", "fear", "disgust", "surprise", "neutral"]

    # Aggregate emotions daily
    agg = (
        df.groupby(['employees_id','date'])[emo_cols]
          .mean()
          .reset_index()
          .rename(columns={c:f"avg_{c}" for c in emo_cols})
    )

    # Volatility calculation
    df['hour'] = df['ts'].dt.hour
    vol = (
        df.groupby(['employees_id','date','hour'])['dominant_emotion']
          .value_counts(normalize=True)
          .unstack(fill_value=0.0)
          .groupby(['employees_id','date'])
          .std()
          .mean(axis=1)
          .reset_index(name="emotion_volatility")
    )

    # Merge
    daily = pd.merge(agg, vol, on=['employees_id','date'], how='left')

    # Percentages
    daily['positive_pct'] = daily['avg_happy'] + daily['avg_surprise']
    daily['negative_pct'] = daily['avg_sad'] + daily['avg_angry'] + daily['avg_fear'] + daily['avg_disgust']
    daily['neutral_pct'] = daily['avg_neutral']

    # Wellness score
    v = daily['emotion_volatility'].fillna(0).clip(0, 0.5)
    vnorm = (v - v.min()) / (v.max() - v.min() + 1e-9)

    daily['wellness_score'] = (
        60 * daily['positive_pct'] + 
        25 * (1 - vnorm) +
        15 * (1 - daily['negative_pct'])
    )

    # -----------------------
    # Insert into DB
    # -----------------------
    conn = get_conn()
    cursor = conn.cursor()

    for _, row in daily.iterrows():
         values = (
        row['employees_id'], row['date'],
        row['avg_happy'], row['avg_sad'], row['avg_angry'], row['avg_fear'],
        row['avg_disgust'], row['avg_surprise'], row['avg_neutral'],
        row['emotion_volatility'], row['positive_pct'],
        row['negative_pct'], row['neutral_pct'], row['wellness_score']
    )
         values= tuple(None if pd.isna(v) else v for v in values)
         
    cursor.execute("""
            INSERT INTO daily_metrices
            (employees_id, date, avg_happy, avg_sad, avg_angry, avg_fear,
             avg_disgust, avg_surprise,avg_neutral,
             emotion_volatility, positive_pct, negative_pct, neutral_pct, wellness_score)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
              avg_happy=VALUES(avg_happy),
              avg_sad=VALUES(avg_sad),
              avg_angry=VALUES(avg_angry),
              avg_fear=VALUES(avg_fear),
              avg_disgust=VALUES(avg_disgust),
              avg_surprise=VALUES(avg_surprise),
              avg_neutral=VALUES(avg_neutral),
              emotion_volatility=VALUES(emotion_volatility),
              positive_pct=VALUES(positive_pct),
              negative_pct=VALUES(negative_pct),
              neutral_pct=VALUES(neutral_pct),
              wellness_score=VALUES(wellness_score)
        """, values)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Daily metrices updated successfully")

# -----------------------
# Run script
# -----------------------
if __name__ == "__main__":
    compute_daily_metrices()
