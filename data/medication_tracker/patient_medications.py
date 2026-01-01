import streamlit as st
import psycopg2
from db.database import get_connection
from datetime import date


def _get_medication_status(start_date, end_date):
	"""Determine medication status ('active' or 'inactive')."""
	today = date.today()
	return 'active' if start_date <= today and (end_date is None or end_date >= today) else 'inactive'


def _build_med_dict(row, include_status=True):
	"""Build medication dict from database row."""
	med = {
		'id': row[0],
		'drug_id': row[1],
		'dose': row[2],
		'instructions': row[3],
		'start_date': row[4],
		'end_date': row[5],
		'prescribed_by': row[6],
		'timing': row[7]
	}
	if include_status:
		med['status'] = _get_medication_status(row[4], row[5])
	return med


def _execute_med_query(query, params, include_status=True):
	"""Execute medication query and return list of dicts."""
	conn = get_connection()
	meds = []
	try:
		with conn.cursor() as cur:
			cur.execute(query, params)
			meds = [_build_med_dict(row, include_status) for row in cur.fetchall()]
	except Exception as e:
		st.session_state['db_fetch_error'] = str(e)
	finally:
		conn.close()
	return meds


def update_patient_medication(patient_med_id, dose, instructions, start_date, end_date, prescribed_by, timing):
	"""Update an existing patient medication entry by ID."""
	conn = get_connection()
	if not conn:
		st.session_state['db_update_error'] = "Failed to connect to database"
		return False
	
	try:
		with conn.cursor() as cur:
			cur.execute('''
				UPDATE patient_medications
				SET dose = %s, instructions = %s, start_date = %s, end_date = %s, prescribed_by = %s, timing = %s
				WHERE patient_med_id = %s
			''', (dose, instructions, start_date, end_date, prescribed_by, timing, patient_med_id))
			conn.commit()
		return True
	except Exception as e:
		st.session_state['db_update_error'] = str(e)
		conn.rollback()
		return False
	finally:
		conn.close()
def get_all_patient_medication_entries(user_id):
	"""Return all medication entries for a user (not distinct by drug_id)."""
	query = '''
		SELECT patient_med_id, drug_id, dose, instructions, start_date, end_date, prescribed_by, timing
		FROM patient_medications
		WHERE user_id = %s
		ORDER BY start_date DESC, drug_id, timing
	'''
	return _execute_med_query(query, (user_id,))


def get_medication_status(start_date, end_date):
	"""Utility: Determine medication status ('active' or 'inactive')."""
	return _get_medication_status(start_date, end_date)


def get_daily_patient_medications(user_id):
	"""Return all active medications for a user."""
	today = date.today()
	query = '''
		SELECT patient_med_id, drug_id, dose, instructions, start_date, end_date, prescribed_by, timing
		FROM patient_medications
		WHERE user_id = %s AND start_date <= %s AND (end_date IS NULL OR end_date >= %s)
		ORDER BY drug_id, timing, start_date DESC
	'''
	return _execute_med_query(query, (user_id, today, today), include_status=False)


def get_all_patient_medications(user_id):
	"""Return one medication per drug_id (most recent by start_date)."""
	query = '''
		SELECT DISTINCT ON (drug_id) patient_med_id, drug_id, dose, instructions, start_date, end_date, prescribed_by, timing
		FROM patient_medications
		WHERE user_id = %s
		ORDER BY drug_id, start_date DESC
	'''
	return _execute_med_query(query, (user_id,))


def get_active_patient_medications(user_id):
	"""Return one active medication per drug_id (most recent by start_date)."""
	today = date.today()
	query = '''
		SELECT DISTINCT ON (drug_id) patient_med_id, drug_id, dose, instructions, start_date, end_date, prescribed_by, timing
		FROM patient_medications
		WHERE user_id = %s AND start_date <= %s AND (end_date IS NULL OR end_date >= %s)
		ORDER BY drug_id, start_date DESC
	'''
	return _execute_med_query(query, (user_id, today, today))


def get_inactive_patient_medications(user_id):
	"""Return one inactive medication per drug_id (most recent by start_date)."""
	today = date.today()
	query = '''
		SELECT DISTINCT ON (drug_id) patient_med_id, drug_id, dose, instructions, start_date, end_date, prescribed_by, timing
		FROM patient_medications
		WHERE user_id = %s AND end_date IS NOT NULL AND end_date < %s
		ORDER BY drug_id, start_date DESC
	'''
	return _execute_med_query(query, (user_id, today))


def get_patient_medications(user_id):
	"""Return one medication per drug_id (most recent by start_date)."""
	query = '''
		SELECT DISTINCT ON (drug_id) patient_med_id, drug_id, dose, instructions, start_date, end_date, prescribed_by, timing
		FROM patient_medications
		WHERE user_id = %s
		ORDER BY drug_id, start_date DESC
	'''
	return _execute_med_query(query, (user_id,), include_status=False)
import psycopg2
from db.database import get_connection

import streamlit as st

def insert_patient_medication(user_id, drug_id, dose, instructions, start_date, end_date, prescribed_by, timing):
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			try:
				cur.execute('''
					INSERT INTO patient_medications (user_id, drug_id, dose, instructions, start_date, end_date, prescribed_by, timing)
					VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
				''', (user_id, drug_id, dose, instructions, start_date, end_date, prescribed_by, timing))
				conn.commit()
			except Exception as e:
				st.session_state['db_insert_error'] = str(e)
				conn.rollback()
	finally:
		conn.close()

def get_patient_medication_entry_by_id(patient_med_id):
    """
    Fetch a single patient_medication entry by its id.
    """
    from db.database import get_connection
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patient_medications WHERE patient_med_id = %s", (patient_med_id,))
    row = cur.fetchone()
    if row:
        # Map columns to dict keys (adjust as needed for your schema)
        columns = [desc[0] for desc in cur.description]
        entry = dict(zip(columns, row))
        cur.close()
        conn.close()
        return entry
    cur.close()
    conn.close()
    return None
