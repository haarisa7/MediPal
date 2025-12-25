import psycopg2
from db.database import get_connection
from datetime import datetime
from data.patient_medications import get_patient_medication_entry_by_id
from data.medications import get_drug_display_name


def _build_request_dict(row, include_patient_name=False, include_clinician_name=True):
    """Build a standardized request dictionary from a database row."""
    request = {
        'request_id': row[0],
        'drug_name': get_drug_display_name(row[2]) if len(row) > 2 else None,
        'dose': row[3],
        'instructions': row[4],
        'timing': row[5] if len(row) > 5 else None,
        'request_type': row[6] if len(row) > 6 else None,
        'patient_med_id': row[7] if len(row) > 7 else None,
        'start_date': row[8] if len(row) > 8 else None,
        'end_date': row[9] if len(row) > 9 else None,
    }
    
    # Add clinician name if included
    if include_clinician_name and len(row) > 11:
        request['prescribed_by'] = f"{row[10]} {row[11]}"
    
    # Add patient name if included
    if include_patient_name and len(row) > 13:
        request['patient_name'] = f"{row[12]} {row[13]}"
        request['patient_id'] = row[1]
    
    # Add status fields if present
    if len(row) > 15:
        request['responded'] = row[14]
        request['approved'] = row[15]
    
    return request


def create_medication_request(patient_id, clinician_id, drug_id, dose, instructions, start_date, end_date, timing, request_type='add', patient_med_id=None):
    """Insert a new medication request into the medication_requests table."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO medication_requests (
                    patient_id, clinician_id, drug_id, dose, instructions, start_date, end_date, timing, request_type, responded, approved, created_at, patient_med_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (patient_id, clinician_id, drug_id, dose, instructions, start_date, end_date, timing, request_type, False, False, datetime.now(), patient_med_id))
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
                SELECT r.request_id, r.patient_id, r.drug_id, r.dose, r.instructions, r.timing, r.request_type, r.patient_med_id, r.start_date, r.end_date, c.first_name, c.last_name, u.first_name, u.last_name
                FROM medication_requests r
                JOIN users u ON r.patient_id = u.user_id
                JOIN users c ON r.clinician_id = c.user_id
                WHERE r.patient_id = %s AND r.responded = FALSE
                ORDER BY r.created_at DESC
            ''', (patient_id,))
            rows = cur.fetchall()
            return [_build_request_dict(row, include_patient_name=True) for row in rows]
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
                SELECT r.request_id, r.patient_id, r.drug_id, r.dose, r.instructions, r.timing, r.request_type, r.patient_med_id, r.start_date, r.end_date, c.first_name, c.last_name
                FROM medication_requests r
                JOIN users c ON r.clinician_id = c.user_id
                WHERE request_id = %s
            ''', (request_id,))
            row = cur.fetchone()
            if row:
                return _build_request_dict(row)
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
    
    if details['request_type'] == 'add':
        from data.patient_medications import insert_patient_medication
        return insert_patient_medication(
            details['patient_id'], details['drug_name'], details['dose'], details['instructions'],
            details['start_date'], details['end_date'], details['prescribed_by'], details['timing']
        )
    elif details['request_type'] == 'edit':
        from data.patient_medications import update_patient_medication
        return update_patient_medication(
            details['patient_med_id'], details['dose'], details['instructions'],
            details['start_date'], details['end_date'], details['prescribed_by'], details['timing']
        )


def get_all_requests_for_clinician(clinician_id):
    """Return all medication requests created by this clinician, with status info and patient name."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT r.request_id, r.patient_id, r.drug_id, r.dose, r.instructions, r.timing, r.request_type, r.patient_med_id, r.start_date, r.end_date, c.first_name, c.last_name, u.first_name, u.last_name, r.responded, r.approved
                FROM medication_requests r
                JOIN users u ON r.patient_id = u.user_id
                JOIN users c ON r.clinician_id = c.user_id
                WHERE r.clinician_id = %s
                ORDER BY r.created_at DESC
            ''', (clinician_id,))
            rows = cur.fetchall()
            return [_build_request_dict(row, include_patient_name=True) for row in rows]
    except Exception as e:
        print("Error fetching clinician requests:", e)
        return []
    finally:
        conn.close()


def compare_medication_entries(old_entry, new_entry):
    """Compare two medication dicts and return a dict of changed fields with (old, new) values."""
    fields = ['dose', 'instructions', 'start_date', 'end_date', 'prescribed_by', 'timing']
    changes = {}
    for field in fields:
        old_val = old_entry.get(field)
        new_val = new_entry.get(field)
        if str(old_val) != str(new_val):
            changes[field] = (old_val, new_val)
    return changes


def get_edit_changes(request):
    """Get changed fields by comparing request with existing patient_med entry."""
    if not request.get('patient_med_id'):
        return {}
    old_entry = get_patient_medication_entry_by_id(request['patient_med_id'])
    return compare_medication_entries(old_entry or {}, request) if old_entry else {}
