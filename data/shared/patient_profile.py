import psycopg2
from db.database import get_connection

def get_user_role(user_id):
    """Return the role (0=patient, 1=clinician) for the given user_id, or None if not found."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT role FROM users WHERE user_id = %s', (user_id,))
            row = cur.fetchone()
            if row:
                return row[0]
    except Exception as e:
        print("Error fetching user role:", e)
    finally:
        conn.close()
    return None


def get_patient_profile(user_id):
    """Get patient profile from database."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT user_id, email, role, first_name, last_name, date_of_birth
                FROM users
                WHERE user_id = %s
            ''', (user_id,))
            row = cur.fetchone()
            if row:
                return {
                    "user_id": row[0],
                    "email": row[1],
                    "role": row[2],
                    "first_name": row[3],
                    "last_name": row[4],
                    "date_of_birth": row[5],
                    "name": f"{row[3]} {row[4]}"
                }
    except Exception as e:
        print("Error fetching patient profile:", e)
    finally:
        conn.close()
    return None