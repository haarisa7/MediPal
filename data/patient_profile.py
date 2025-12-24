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
def get_patient_profile_db(user_id):
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
# Demo patient profile data for Emergency Dashboard
from datetime import datetime, date

PATIENT_PROFILE = {
    "name": "John A. Smith",
    "age": 45,
    "date_of_birth": "1979-03-15",
    "blood_type": "O+",
    "weight": "180 lbs",
    "height": "5'10\"",
    "medical_id": "MED-2024-001",
    "emergency_contact": {
        "name": "Jane Smith",
        "phone": "(555) 123-4567", 
        "relation": "Spouse",
        "email": "jane.smith@email.com"
    },
    "secondary_contact": {
        "name": "Michael Smith", 
        "phone": "(555) 987-6543",
        "relation": "Son",
        "email": "michael.smith@email.com"
    },
    "primary_doctor": {
        "name": "Dr. Alice Johnson",
        "phone": "(555) 234-5678",
        "specialty": "Internal Medicine",
        "hospital": "City General Hospital"
    },
    "insurance": {
        "provider": "Blue Cross Blue Shield",
        "id": "BC123456789",
        "group": "EMP001"
    },
    "last_updated": datetime.now().isoformat()
}

MEDICAL_CONDITIONS = [
    {
        "id": 1,
        "name": "Hypertension",
        "severity": "moderate", 
        "diagnosed_date": "2020-03-15",
        "status": "controlled",
        "doctor_id": 1,
        "notes": "Well controlled with medication"
    },
    {
        "id": 2,
        "name": "Type 2 Diabetes",
        "severity": "mild",
        "diagnosed_date": "2019-08-20", 
        "status": "managed",
        "doctor_id": 2,
        "notes": "Diet controlled, regular monitoring"
    },
    {
        "id": 3,
        "name": "High Cholesterol",
        "severity": "moderate",
        "diagnosed_date": "2021-01-10",
        "status": "treated", 
        "doctor_id": 1,
        "notes": "Responding well to statin therapy"
    }
]

MEDICAL_ALERTS = [
    {
        "id": 1,
        "type": "allergy",
        "substance": "Penicillin",
        "reaction": "Severe rash, difficulty breathing",
        "severity": "critical",
        "date_discovered": "2015-06-12"
    },
    {
        "id": 2,
        "type": "allergy", 
        "substance": "Shellfish",
        "reaction": "Hives, swelling",
        "severity": "moderate",
        "date_discovered": "2010-04-08"
    },
    {
        "id": 3,
        "type": "interaction",
        "drugs": ["Atorvastatin", "Warfarin"],
        "warning": "Monitor for increased bleeding risk",
        "severity": "moderate", 
        "date_noted": "2023-02-15"
    }
]


def get_patient_profile(user_id=None):
    if user_id is not None:
        db_profile = get_patient_profile_db(user_id)
        if db_profile:
            return db_profile
    return PATIENT_PROFILE.copy()


def get_medical_conditions():
    return [c.copy() for c in MEDICAL_CONDITIONS]


def get_medical_alerts():
    return [a.copy() for a in MEDICAL_ALERTS]


def get_critical_alerts():
    """Return only critical/severe alerts for emergency display"""
    return [a for a in MEDICAL_ALERTS if a.get('severity') == 'critical']