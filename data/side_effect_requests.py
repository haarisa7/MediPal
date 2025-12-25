from db.database import get_connection


def _build_note_dict(row):
	"""Build note dict from database row."""
	return {
		'request_id': row[0],
		'report_id': row[1],
		'clinician_id': row[2],
		'patient_id': row[3],
		'doctor_note': row[4],
		'received': row[5],
		'sent_at': row[6],
		'doctor_first_name': row[7],
		'doctor_last_name': row[8]
	}


_NOTE_QUERY = '''
	SELECT 
		ser.request_id,
		ser.report_id,
		ser.clinician_id,
		ser.patient_id,
		ser.doctor_note,
		ser.received,
		ser.sent_at,
		u.first_name,
		u.last_name
	FROM side_effect_requests ser
	LEFT JOIN users u ON ser.clinician_id = u.user_id
'''


def insert_doctor_note(report_id, clinician_id, patient_id, doctor_note):
    """
    Insert a doctor's note for a side effect report.
    
    Args:
        report_id: ID of the side effect report
        clinician_id: ID of the clinician sending the note
        patient_id: ID of the patient receiving the note
        doctor_note: The note text from the doctor
    
    Returns:
        request_id of the newly inserted note, or None if failed
    """
    conn = get_connection()
    request_id = None
    
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO side_effect_requests 
                (report_id, clinician_id, patient_id, doctor_note)
                VALUES (%s, %s, %s, %s)
                RETURNING request_id
            ''', (report_id, clinician_id, patient_id, doctor_note))
            
            result = cur.fetchone()
            if result:
                request_id = result[0]
            
            conn.commit()
    except Exception as e:
        print(f"Error inserting doctor note: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    return request_id


def get_doctor_notes_for_report(report_id):
	"""Get all doctor notes for a specific side effect report."""
	conn = get_connection()
	notes = []
	
	try:
		with conn.cursor() as cur:
			cur.execute(_NOTE_QUERY + 'WHERE ser.report_id = %s ORDER BY ser.sent_at DESC', (report_id,))
			notes = [_build_note_dict(row) for row in cur.fetchall()]
	except Exception as e:
		print(f"Error fetching doctor notes for report: {e}")
	finally:
		conn.close()
	
	return notes


def get_unread_doctor_notes_for_patient(patient_id):
    """
    Get count of unread doctor notes for a patient.
    
    Args:
        patient_id: ID of the patient
    
    Returns:
        Integer count of unread notes
    """
    conn = get_connection()
    count = 0
    
    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT COUNT(*) 
                FROM side_effect_requests 
                WHERE patient_id = %s AND received = FALSE
            ''', (patient_id,))
            
            result = cur.fetchone()
            if result:
                count = result[0]
    except Exception as e:
        print(f"Error fetching unread doctor notes count: {e}")
    finally:
        conn.close()
    
    return count


def mark_all_notes_as_received(patient_id):
    """
    Mark all doctor notes for a patient as received when they view Side Effects page.
    
    Args:
        patient_id: ID of the patient
    
    Returns:
        Number of notes marked as received
    """
    conn = get_connection()
    count = 0
    
    try:
        with conn.cursor() as cur:
            cur.execute('''
                UPDATE side_effect_requests 
                SET received = TRUE 
                WHERE patient_id = %s AND received = FALSE
                RETURNING request_id
            ''', (patient_id,))
            
            results = cur.fetchall()
            count = len(results)
            conn.commit()
    except Exception as e:
        print(f"Error marking notes as received: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    return count


def get_all_notes_for_patient_reports(patient_id):
	"""Get all doctor notes for all of a patient's side effect reports."""
	conn = get_connection()
	notes_by_report = {}
	
	try:
		with conn.cursor() as cur:
			cur.execute(_NOTE_QUERY + 'WHERE ser.patient_id = %s ORDER BY ser.sent_at DESC', (patient_id,))
			
			for row in cur.fetchall():
				note = _build_note_dict(row)
				report_id = note['report_id']
				
				if report_id not in notes_by_report:
					notes_by_report[report_id] = []
				notes_by_report[report_id].append(note)
				
	except Exception as e:
		print(f"Error fetching all patient notes: {e}")
	finally:
		conn.close()
	
	return notes_by_report
