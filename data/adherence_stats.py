from db.database import get_connection
from data.patient_medications import get_daily_patient_medications
from data.medication_log import get_today_intake_status
from datetime import date


def _calculate_adherence_rate(logs):
	"""Calculate adherence rate from intake logs."""
	if not logs:
		return None
	taken_count = sum(1 for row in logs if row[0])
	return round(100 * taken_count / len(logs))


def get_today_summary_for_user(user_id):
	"""Get today's adherence summary for a user."""
	meds = get_daily_patient_medications(user_id)
	total = len(meds)
	taken = sum(1 for med in meds if get_today_intake_status(med['id']) == 'taken')
	missed = sum(1 for med in meds if get_today_intake_status(med['id']) == 'missed')
	remaining = total - taken - missed
	completion_rate = int((taken / total) * 100) if total > 0 else 0
	
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
	"""Return overall adherence rate (0-100) for all medications for a user."""
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			cur.execute('SELECT patient_med_id FROM patient_medications WHERE user_id = %s', (user_id,))
			patient_med_ids = [row[0] for row in cur.fetchall()]
			if not patient_med_ids:
				return None
			
			cur.execute('SELECT taken FROM medication_intake_log WHERE patient_med_id = ANY(%s)', (patient_med_ids,))
			return _calculate_adherence_rate(cur.fetchall())
	finally:
		conn.close()


def get_overall_adherence_for_med_id(med_id):
	"""Return adherence rate (0-100) for all patient_med rows with this med_id."""
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			cur.execute('SELECT patient_med_id FROM patient_medications WHERE drug_id = %s', (med_id,))
			patient_med_ids = [row[0] for row in cur.fetchall()]
			if not patient_med_ids:
				return None
			
			cur.execute('SELECT taken FROM medication_intake_log WHERE patient_med_id = ANY(%s)', (patient_med_ids,))
			return _calculate_adherence_rate(cur.fetchall())
	finally:
		conn.close()


def get_adherence_for_patient_med_id(patient_med_id):
	"""Return adherence rate (0-100) for a specific patient_med_id."""
	conn = get_connection()
	try:
		with conn.cursor() as cur:
			cur.execute('SELECT taken FROM medication_intake_log WHERE patient_med_id = %s', (patient_med_id,))
			return _calculate_adherence_rate(cur.fetchall())
	finally:
		conn.close()
