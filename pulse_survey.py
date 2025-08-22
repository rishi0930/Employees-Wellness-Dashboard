import mysql.connector as mys
from datetime import date
from tkinter import messagebox
import tkinter as tk

def get_conn():
    return mys.connect(host="localhost",user="root",password="1234",database="wellness_db")

def submit_survey(emp_id, mood, stress, energy, note):
    today=date.today()
    try:
        conn=get_conn()
        cursor=conn.cursor()

        cursor.execute("""
            INSERT INTO pulse_survey (employees_id, date, mood_1_5, stress_1_5, energy_1_5, note)
            VALUES (%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                mood_1_5=VALUES(mood_1_5),
                stress_1_5=VALUES(stress_1_5),
                energy_1_5=VALUES(energy_1_5),
                note=VALUES(note)
        """, (emp_id, today, mood, stress, energy, note))
        conn.commit()
        cursor.close()
        conn.close()

        messagebox.showinfo("Success","Pulse survey submitted successfully!")
    except Exception as e:
        messagebox.showerror("Error",f"Failed to Submit survey\n{e}")

# ---------- Survey Window ----------
def survey_window(emp_id):
    survey=tk.Toplevel()
    survey.title("Daily Pulse Survey")
    survey.geometry("400x350")
    survey.config(bg="#f7f7f7")
    
    tk.Label(survey,text=f"Employee ID:{emp_id}", font=("Times New Roman",12,"bold"),bg='#f7f7f7').pack(pady=10)

    #Mood
    tk.Label(survey,text="Mood(1=Very Bad, 5=Very Good):",bg="#f7f7f7").pack()
    mood_var=tk.IntVar(value=3)
    tk.Spinbox(survey, from_=1,to=5, textvariable=mood_var).pack()

    #Energy
    tk.Label(survey, text="Energy(1=Exhausted, 5=Very Energetic):",bg="#f7f7f7").pack()
    energy_var=tk.IntVar(value=3)
    tk.Spinbox(survey, from_=1, to=5, textvariable=energy_var).pack()

    #Stress
    tk.Label(survey, text="Stress (1=No stress, 5=Very high):", bg="#f7f7f7").pack()
    stress_var = tk.IntVar(value=3)
    tk.Spinbox(survey, from_=1, to=5, textvariable=stress_var).pack()

    #Notes
    tk.Label(survey, text="Notes", bg="#f7f7f7").pack()
    note_entry=tk.Text(survey, height=4, width=30)
    note_entry.pack()

    #Submit button
    def on_submit():
        mood=mood_var.get()
        stress=stress_var.get()
        energy=energy_var.get()
        note=note_entry.get("1.0",tk.END).strip()
        submit_survey(emp_id, mood, stress, energy, note)

    tk.Button(survey, text="Submit Survey", bg="#4CAF50",fg="white",command=on_submit).pack(pady=10)

#---------- Login Window ----------
def login_window():
    root=tk.Tk()
    root.title("Employee Login")
    root.geometry("300x200")
    root.config(bg='#f7f7f7')

    tk.Label(root, text="Enter Employee ID:", bg="#f7f7f7").pack(pady=10)
    emp_var=tk.StringVar()
    tk.Entry(root, textvariable=emp_var).pack()

    def login():
        emp_id=emp_var.get().strip()
        if not emp_id:
            messagebox.showwarning("Input Error","Employee ID is required")
            return
        
        conn=get_conn()
        cursor=conn.cursor()
        cursor.execute("SELECT employees_id FROM employees WHERE employees_id=%s",(emp_id,))
        result=cursor.fetchone()
        conn.close()

        if result:
            root.withdraw()
            survey_window(emp_id)
        else:
            messagebox.showerror("Login Failed", "Invalid Employee ID")

    tk.Button(root, text="Login",command=login, bg="#2196F3",fg="white").pack(pady=10)

    root.mainloop()

if __name__=="__main__":
    login_window()