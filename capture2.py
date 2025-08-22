import cv2, uuid, time, threading
from deepface import DeepFace
import mysql.connector as mys
from datetime import datetime, timezone
import tkinter as tk
from tkinter import messagebox, scrolledtext

# ------------------- DB Connection -------------------
def get_conn():
    return mys.connect(
        host="localhost",
        user="root",
        password="1234",
        database="wellness_db"
    )

def employee_exists(employee_id: str) -> bool:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM employees WHERE employees_id=%s", (employee_id,))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists

def add_employee(employee_id: str, alias: str, team: str, job_role: str):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO employees (employees_id, display_alias, team, job_role, consent_ts)
        VALUES (%s, %s, %s, %s, %s)
    """, (employee_id, alias, team, job_role, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()

# ------------------- Session Management -------------------
def new_session(employee_id: str) -> str:
    session_id = str(uuid.uuid4())
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sessions(session_id, employees_id, device_id, start_ts) VALUES (%s,%s,%s,%s)",
        (session_id, employee_id, "laptop_cam", datetime.now(timezone.utc))
    )
    conn.commit()
    cursor.close()
    conn.close()
    return session_id

def end_session(session_id: str):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE sessions SET end_ts=%s WHERE session_id=%s",
        (datetime.now(timezone.utc), session_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

# ------------------- Logging Emotions -------------------
def log_emotion(session_id: str, result: dict):
    conn = get_conn()
    cursor = conn.cursor()
    emotion = result['dominant_emotion']
    scores = result['emotion']
    clean_scores = {k: float(v) for k, v in scores.items()}
    cursor.execute("""
        INSERT INTO face_events 
        (session_id, ts, dominant_emotion, happy, sad, angry, fear, disgust, surprise, neutral, face_conf) 
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        session_id,
        datetime.now(timezone.utc),
        emotion,
        clean_scores.get("happy", 0.0),
        clean_scores.get("sad", 0.0),
        clean_scores.get("angry", 0.0),
        clean_scores.get("fear", 0.0),
        clean_scores.get("disgust", 0.0),
        clean_scores.get("surprise", 0.0),
        clean_scores.get("neutral", 0.0),
        float(result.get("face_confidence", 1.0))
    ))
    conn.commit()
    cursor.close()
    conn.close()
    log(f"Logged: {emotion}")

# ------------------- Capture Process -------------------
capturing_flag = False
current_session_id = None

def capturing(employee_id: str, sample_every_sec: int = 5, show_preview=True):
    global capturing_flag, current_session_id
    capturing_flag = True
    current_session_id = new_session(employee_id)
    cap = cv2.VideoCapture(0)
    last = 0
    try:
        while capturing_flag:
            ok, frame = cap.read()
            if not ok:
                break
            now = time.time()
            if now - last >= sample_every_sec:
                try:
                    result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                    if isinstance(result, list):
                        result = result[0]
                    log_emotion(current_session_id, result)
                except Exception as e:
                    log(f"DeepFace error: {e}")
                last = now
            if show_preview:
                cv2.imshow("Wellness Capture (press q in window to quit)", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        end_session(current_session_id)
        capturing_flag = False
        log("[INFO] Session ended.")

# ------------------- Tkinter GUI -------------------
def start_capture():
    emp_id = entry_emp.get().strip()
    alias = entry_alias.get().strip()
    team = entry_team.get().strip()
    job_role = entry_job.get().strip()

    if not emp_id:
        messagebox.showerror("Error", "Employee ID is required")
        return

    if employee_exists(emp_id):
        log(f"[INFO] Employee {emp_id} already exists. Starting capture directly...")
        threading.Thread(target=capturing, args=(emp_id,), daemon=True).start()
    else:
        if not alias or not team or not job_role:
            messagebox.showerror("Error", "New employee: please fill alias, team, job role")
            return
        add_employee(emp_id, alias, team, job_role)
        log(f"[INFO] ✅ New employee {emp_id} added. Starting capture...")
        threading.Thread(target=capturing, args=(emp_id,), daemon=True).start()

def stop_capture():
    global capturing_flag
    capturing_flag = False
    log("[INFO] Stopping capture...")

def log(msg: str):
    text_log.insert(tk.END, msg + "\n")
    text_log.see(tk.END)

# Tkinter Window
root = tk.Tk()
root.title("Employee Wellness Capture")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

tk.Label(frame, text="Employee ID:").grid(row=0, column=0, sticky="w")
entry_emp = tk.Entry(frame, width=20)
entry_emp.grid(row=0, column=1)

tk.Label(frame, text="Display Alias:").grid(row=1, column=0, sticky="w")
entry_alias = tk.Entry(frame, width=20)
entry_alias.grid(row=1, column=1)

tk.Label(frame, text="Team:").grid(row=2, column=0, sticky="w")
entry_team = tk.Entry(frame, width=20)
entry_team.grid(row=2, column=1)

tk.Label(frame, text="Job Role:").grid(row=3, column=0, sticky="w")
entry_job = tk.Entry(frame, width=20)
entry_job.grid(row=3, column=1)

btn_start = tk.Button(frame, text="Start Capture", command=start_capture, bg="green", fg="white")
btn_start.grid(row=4, column=0, pady=5)

btn_stop = tk.Button(frame, text="Stop Capture", command=stop_capture, bg="red", fg="white")
btn_stop.grid(row=4, column=1, pady=5)

text_log = scrolledtext.ScrolledText(root, width=70, height=15)
text_log.pack(pady=10)

root.mainloop()
