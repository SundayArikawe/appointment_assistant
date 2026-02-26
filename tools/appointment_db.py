import sqlite3
from datetime import datetime
import uuid

DB_NAME = "appointments.db"


def get_conn():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        appointment_id TEXT PRIMARY KEY,
        patient_name TEXT NOT NULL,
        department TEXT NOT NULL,
        appointment_date TEXT NOT NULL,
        status TEXT NOT NULL
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM appointments")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
        INSERT INTO appointments VALUES (?, ?, ?, ?, ?)
        """, [
            ("APT-101", "Zack", "MRI", "2026-03-24", "Scheduled"),
            ("APT-102", "Maria", "CT Scan", "2026-04-02", "Scheduled"),
        ])

    conn.commit()
    conn.close()


init_db()


def normalize_date(date_str):
    try:
        parsed = datetime.strptime(date_str, "%d %B %Y")
        return parsed.strftime("%Y-%m-%d")
    except:
        return date_str


def get_active_appointment(user):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT appointment_id, department, appointment_date
    FROM appointments
    WHERE LOWER(patient_name)=LOWER(?) AND status='Scheduled'
    LIMIT 1
    """, (user,))

    row = cursor.fetchone()
    conn.close()
    return row


def create_appointment(user, department, date):
    conn = get_conn()
    cursor = conn.cursor()

    appointment_id = "APT-" + str(uuid.uuid4())[:6]
    iso = normalize_date(date)

    cursor.execute("""
    INSERT INTO appointments VALUES (?, ?, ?, ?, 'Scheduled')
    """, (appointment_id, user, department, iso))

    conn.commit()
    conn.close()

    return iso


def reschedule(user, new_date):
    appointment = get_active_appointment(user)
    if not appointment:
        return None

    appointment_id, dept, old_date = appointment
    iso = normalize_date(new_date)

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE appointments SET appointment_date=? WHERE appointment_id=?
    """, (iso, appointment_id))
    conn.commit()
    conn.close()

    return dept, old_date, iso


def cancel(user):
    appointment = get_active_appointment(user)
    if not appointment:
        return None

    appointment_id, dept, date = appointment

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE appointments SET status='Cancelled' WHERE appointment_id=?
    """, (appointment_id,))
    conn.commit()
    conn.close()

    return dept, date