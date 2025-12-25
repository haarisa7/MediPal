from db.database import get_connection

def _execute_query(query, params=None, fetch_one=False):
	"""Execute query and return results as list of dicts or single dict."""
	conn = get_connection()
	results = [] if not fetch_one else None
	
	try:
		with conn.cursor() as cur:
			cur.execute(query, params or ())
			rows = cur.fetchall()
			
			if fetch_one:
				results = rows[0] if rows else None
			else:
				results = rows
	except Exception as e:
		print(f"Error executing query: {e}")
	finally:
		conn.close()
	
	return results


def get_sideeffects_by_rarity(drug_id, rarity='common'):
	"""Get side effects by rarity for a drug."""
	# Set frequency bounds based on rarity
	if rarity == 'common':
		freq_min, freq_max = 0.5, 1.0
	elif rarity == 'uncommon':
		freq_min, freq_max = 0.2, 0.5
	elif rarity == 'rare':
		freq_min, freq_max = 0.0, 0.2
	else:
		raise ValueError("rarity must be 'common', 'uncommon', or 'rare'")
	
	query = '''
		SELECT se.pt_name, dse.average_frequency
		FROM drug_side_effects dse
		JOIN side_effects se ON dse.side_effect_id = se.meddra_id
		WHERE dse.drug_id = %s AND dse.average_frequency > %s AND dse.average_frequency <= %s
		ORDER BY dse.average_frequency DESC
	'''
	
	rows = _execute_query(query, (drug_id, freq_min, freq_max))
	return [{'pt_name': row[0], 'average_frequency': row[1]} for row in rows]


def get_all_sideeffects_for_drug(drug_id):
	"""Get all side effects for a drug."""
	query = '''
		SELECT se.pt_name, dse.average_frequency
		FROM drug_side_effects dse
		JOIN side_effects se ON dse.side_effect_id = se.meddra_id
		WHERE dse.drug_id = %s
		ORDER BY dse.average_frequency DESC
	'''
	
	rows = _execute_query(query, (drug_id,))
	return [{'pt_name': row[0], 'average_frequency': row[1]} for row in rows]


def search_all_side_effects(search_term=''):
	"""Search side effects by name."""
	if search_term:
		query = '''
			SELECT DISTINCT se.pt_name
			FROM side_effects se
			WHERE LOWER(se.pt_name) LIKE LOWER(%s)
			ORDER BY se.pt_name
			LIMIT 50
		'''
		params = (f'%{search_term}%',)
	else:
		query = '''
			SELECT DISTINCT se.pt_name
			FROM side_effects se
			ORDER BY se.pt_name
			LIMIT 50
		'''
		params = None
	
	rows = _execute_query(query, params)
	return [row[0] for row in rows]


def get_side_effect_id_by_name(pt_name):
	"""Get meddra_id for a side effect by PT name."""
	query = '''
		SELECT meddra_id
		FROM side_effects
		WHERE LOWER(pt_name) = LOWER(%s)
		LIMIT 1
	'''
	
	row = _execute_query(query, (pt_name,), fetch_one=True)
	return row[0] if row else None