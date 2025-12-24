import psycopg2
from db.database import get_connection
from datetime import datetime
from data.patient_medications import get_patient_medication_entry_by_id
from data.medications import get_drug_display_name

def create_medication_request(patient_id, clinician_id, drug_id, dose, instructions, start_date, end_date, timing, request_type='add', patient_med_id=None):
    """
    Insert a new medication request into the medication_requests table.
    Returns True if successful, False otherwise.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO medication_requests (
                    patient_id, clinician_id, drug_id, dose, instructions, start_date, end_date, timing, request_type, responded, approved, created_at, patient_med_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                patient_id,
                clinician_id,
                drug_id,
                dose,
                instructions,
                start_date,
                end_date,
                timing,
                request_type,
                False,  # responded
                False,  # approved
                datetime.now(),
                patient_med_id
            ))
            conn.commit()
        return True
    except Exception as e:
        print("Error creating medication request:", e)
        return False
    finally:
        conn.close()

def get_pending_requests_for_patient(patient_id):
    """Return a list of pending medication requests for the given patient."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT r.request_id, r.drug_id, r.dose, r.instructions, r.timing, r.request_type, r.patient_med_id, r.start_date, r.end_date, c.first_name, c.last_name, u.first_name, u.last_name
                FROM medication_requests r
                JOIN users u ON r.patient_id = u.user_id
                JOIN users c ON r.clinician_id = c.user_id
                WHERE r.patient_id = %s AND r.responded = FALSE
                ORDER BY r.created_at DESC
            ''', (patient_id,))
            rows = cur.fetchall()
            return [
                {
                    'request_id': row[0],
                    'drug_name': get_drug_display_name(row[1]),
                    'dose': row[2],
                    'instructions': row[3],
                    'timing': row[4],
                    'request_type': row[5],
                    'patient_med_id': row[6],
                    'start_date': row[7],
                    'end_date': row[8],
                    'prescribed_by': f"{row[9]} {row[10]}",
                    'patient_name': f"{row[11]} {row[12]}",
                    'patient_id': patient_id
                }
                for row in rows
            ]
    except Exception as e:
        print("Error fetching pending medication requests:", e)
        return []
    finally:
        conn.close()

def respond_to_medication_request(request_id, approved):
    """Mark a medication request as responded and set approved status."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                UPDATE medication_requests
                SET responded = TRUE, approved = %s, responded_at = NOW()
                WHERE request_id = %s
            ''', (approved, request_id))
            conn.commit()
        return True
    except Exception as e:
        print("Error responding to medication request:", e)
        return False
    finally:
        conn.close()

def get_request_details(request_id):
    """Return all details for a medication request."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT patient_id, clinician_id, drug_id, dose, instructions, start_date, end_date, timing, request_type, patient_med_id, c.first_name, c.last_name
                FROM medication_requests r
                JOIN users c ON r.clinician_id = c.user_id
                WHERE request_id = %s
            ''', (request_id,))
            row = cur.fetchone()
            if row:
                return {
                    'patient_id': row[0],
                    'clinician_id': row[1],
                    'drug_name': get_drug_display_name(row[2]),
                    'dose': row[3],
                    'instructions': row[4],
                    'start_date': row[5],
                    'end_date': row[6],
                    'timing': row[7],
                    'request_type': row[8],
                    'patient_med_id': row[9],
                    'prescribed_by': f"{row[10]} {row[11]}"
                }
            return None
    except Exception as e:
        print("Error fetching request details:", e)
        return None
    finally:
        conn.close()

def process_accepted_request(request_id):
    """If accepted, carry out the request (add/edit medication)."""
    details = get_request_details(request_id)
    if not details:
        return False
    from data.patient_medications import insert_patient_medication
    if details['request_type'] == 'add':
        return insert_patient_medication(
            details['patient_id'],
            details['drug_name'],
            details['dose'],
            details['instructions'],
            details['start_date'],
            details['end_date'],
            details['prescribed_by'],
            details['timing']
        )
    elif details['request_type'] == 'edit':
        from data.patient_medications import update_patient_medication
        return update_patient_medication(
            details['patient_med_id'],
            details['dose'],
            details['instructions'],
            details['start_date'],
            details['end_date'],
            details['prescribed_by'],
            details['timing']
        )


def get_all_requests_for_clinician(clinician_id):
    """Return all medication requests created by this clinician, with status info and patient name."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT r.request_id, r.patient_id, r.drug_id, r.dose, r.instructions, r.timing, r.responded, r.approved, r.request_type, r.patient_med_id, r.start_date, r.end_date, u.first_name, u.last_name, c.first_name, c.last_name
                FROM medication_requests r
                JOIN users u ON r.patient_id = u.user_id
                JOIN users c ON r.clinician_id = c.user_id
                WHERE r.clinician_id = %s
                ORDER BY r.created_at DESC
            ''', (clinician_id,))
            rows = cur.fetchall()
            return [
                {
                    'request_id': row[0],
                    'patient_id': row[1],
                    'drug_name': get_drug_display_name(row[2]),
                    'dose': row[3],
                    'instructions': row[4],
                    'timing': row[5],
                    'responded': row[6],
                    'approved': row[7],
                    'request_type': row[8],
                    'patient_med_id': row[9],
                    'start_date': row[10],
                    'end_date': row[11],
                    'patient_name': f"{row[12]} {row[13]}",
                    'prescribed_by': f"{row[14]} {row[15]}"
                }
                for row in rows
            ]
    except Exception as e:
        print("Error fetching clinician requests:", e)
        return []
    finally:
        conn.close()

def compare_medication_entries(old_entry, new_entry):
    """
    Compare two medication dicts and return a dict of changed fields with (old, new) values.
    Only compares relevant fields: dose, instructions, start_date, end_date, prescribed_by, timing.
    """
    import logging
    fields = ['dose', 'instructions', 'start_date', 'end_date', 'prescribed_by', 'timing']
    changes = {}
    for field in fields:
        old_val = old_entry.get(field)
        new_val = new_entry.get(field)
        if str(old_val) != str(new_val):
            changes[field] = (old_val, new_val)
    return changes

def get_edit_changes(request):
    """
    Given a request dict, fetch the old patient_med entry and compare with the request to get changed fields.
    Returns a dict of changed fields with (old, new) values.
    """
    old_entry = None
    if 'patient_med_id' in request and request['patient_med_id']:
        old_entry = get_patient_medication_entry_by_id(request['patient_med_id'])
    changes = compare_medication_entries(old_entry or {}, request) if old_entry else {}
    return changes
