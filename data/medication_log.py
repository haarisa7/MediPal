def get_today_intake_status(patient_med_id, date_for=None):
	"""Return 'taken', 'missed', or None for today's intake status."""
	from datetime import date as dtdate
	date_for = date_for or dtdate.today()
	logs = get_intake_log_for_med(patient_med_id)
	for log in logs:
		if log['taken_time'].date() == date_for:
			return 'taken' if log['taken'] else 'missed'
	return None


def log_missed_intakes_for_day(user_id, date_for=None):
    """
    For the given user and date, log missed intakes for all active meds that have no intake log for that day.
    Should be called at end of day (e.g., by a scheduled job or from medication_tracker).
    """
    from datetime import date as dtdate, datetime, time as dttime
    date_for = date_for or dtdate.today()
    # 1. Get all active patient_med_ids for today
    daily_meds = get_daily_patient_medications(user_id)
    all_ids = [m['id'] for m in daily_meds]
    if not all_ids:
        return 0
    # 2. Get all intake logs for today for these meds
    conn = get_connection()
    logged_ids = set()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT patient_med_id FROM medication_intake_log
                WHERE patient_med_id = ANY(%s) AND DATE(taken_time) = %s
            ''', (all_ids, date_for))
            rows = cur.fetchall()
            logged_ids = set(row[0] for row in rows)
    except Exception as e:
        st.session_state['db_fetch_error'] = str(e)
    finally:
        conn.close()
    # 3. Find missing
    missing_ids = [mid for mid in all_ids if mid not in logged_ids]
    if missing_ids:
        # Use end of day timestamp
        end_of_day = datetime.combine(date_for, dttime(23,59,59))
        log_bulk_missed_intakes(missing_ids, end_of_day)
    return len(missing_ids)
import psycopg2
from db.database import get_connection
import streamlit as st
from datetime import datetime
from data.patient_medications import get_daily_patient_medications


def log_medication_intake(patient_med_id, taken, taken_time=None):
    """Insert a row into medication_intake_log for a medication event (taken or missed)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO medication_intake_log (patient_med_id, taken, taken_time)
                VALUES (%s, %s, %s)
            ''', (patient_med_id, taken, taken_time or datetime.now()))
            conn.commit()
    except Exception as e:
        st.session_state['db_insert_error'] = str(e)
        conn.rollback()
    finally:
        conn.close()

def log_bulk_missed_intakes(patient_med_ids, date_for=None):
    """Insert missed rows for all patient_med_ids for a given day (e.g., at end of day for untaken meds)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for med_id in patient_med_ids:
                cur.execute('''
                    INSERT INTO medication_intake_log (patient_med_id, taken, taken_time)
                    VALUES (%s, %s, %s)
                ''', (med_id, False, date_for or datetime.now()))
            conn.commit()
    except Exception as e:
        st.session_state['db_insert_error'] = str(e)
        conn.rollback()
    finally:
        conn.close()

def get_intake_log_for_med(patient_med_id):
	"""Return all intake log rows for a given patient_med_id."""
	conn = get_connection()
	logs = []
	try:
		with conn.cursor() as cur:
			cur.execute('''
				SELECT intake_id, patient_med_id, taken, taken_time
				FROM medication_intake_log
				WHERE patient_med_id = %s
				ORDER BY taken_time DESC
			''', (patient_med_id,))
			rows = cur.fetchall()
			for row in rows:
				logs.append({
					'intake_id': row[0],
					'patient_med_id': row[1],
					'taken': row[2],
					'taken_time': row[3]
				})
	except Exception as e:
		st.session_state['db_fetch_error'] = str(e)
	finally:
		conn.close()
	return logs
