from data.patient_medications import get_daily_patient_medications
from data.medication_log import get_today_intake_status
from datetime import date

def get_today_summary_for_user(user_id):
	"""
	Returns a dict with keys: taken, total, remaining, overdue, completion_rate
	for the given user for today.
	"""
	meds = get_daily_patient_medications(user_id)
	total = len(meds)
	taken = 0
	missed = 0
	for med in meds:
		status = get_today_intake_status(med['id'])
		if status == 'taken':
			taken += 1
		elif status == 'missed':
			missed += 1
	remaining = total - taken - missed
	completion_rate = int((taken / total) * 100) if total > 0 else 0
	# Get active medications
	from data.patient_medications import get_active_patient_medications
	active_meds = len(get_active_patient_medications(user_id))
	return {
		'taken': taken,
		'total': total,
		'remaining': remaining,
		'overdue': missed,
		'active_meds': active_meds,
		'completion_rate': completion_rate
	}
def get_total_adherence_for_user(user_id):
	"""Return overall adherence rate (0-100) for all patient_med rows for a user (all time, all drugs/timings)."""
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			cur.execute('SELECT patient_med_id FROM patient_medications WHERE user_id = %s', (user_id,))
			patient_med_ids = [row[0] for row in cur.fetchall()]
			if not patient_med_ids:
				return None
			cur.execute('SELECT taken FROM medication_intake_log WHERE patient_med_id = ANY(%s)', (patient_med_ids,))
			logs = cur.fetchall()
			if not logs:
				return None
			taken_count = sum(1 for row in logs if row[0])
			total_count = len(logs)
			return round(100 * taken_count / total_count)
	finally:
		conn.close()
from db.database import get_connection

def get_overall_adherence_for_med_id(med_id):
	"""Return adherence rate (0-100) for all patient_med rows with this med_id (all timings, all time)."""
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			# Get all patient_med_ids for this med_id
			cur.execute('SELECT patient_med_id FROM patient_medications WHERE drug_id = %s', (med_id,))
			patient_med_ids = [row[0] for row in cur.fetchall()]
			if not patient_med_ids:
				return None
			# Get all intake logs for these patient_med_ids
			cur.execute('''
				SELECT taken FROM medication_intake_log WHERE patient_med_id = ANY(%s)
			''', (patient_med_ids,))
			logs = cur.fetchall()
			if not logs:
				return None
			taken_count = sum(1 for row in logs if row[0])
			total_count = len(logs)
			return round(100 * taken_count / total_count)
	finally:
		conn.close()

def get_adherence_for_patient_med_id(patient_med_id):
	"""Return adherence rate (0-100) for a specific patient_med_id (med+timing, all time)."""
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			cur.execute('SELECT taken FROM medication_intake_log WHERE patient_med_id = %s', (patient_med_id,))
			logs = cur.fetchall()
			if not logs:
				return None
			taken_count = sum(1 for row in logs if row[0])
			total_count = len(logs)
			return round(100 * taken_count / total_count)
	finally:
		conn.close()
