from db.database import get_connection

def get_sideeffects_by_rarity(drug_id, rarity='common'):
	"""
	Returns a list of dicts with 'pt_name' (side effect name) and 'average_frequency' for side effects
	associated with the given drug_id, filtered by rarity:
	- 'common': average_frequency > 0.5
	- 'uncommon': 0.2 < average_frequency <= 0.5
	- 'rare': average_frequency <= 0.2
	"""
	conn = get_connection()
	side_effects = []
	# Set frequency bounds based on rarity
	if rarity == 'common':
		freq_min, freq_max = 0.5, 1.0
	elif rarity == 'uncommon':
		freq_min, freq_max = 0.2, 0.5
	elif rarity == 'rare':
		freq_min, freq_max = 0.0, 0.2
	else:
		raise ValueError("rarity must be 'common', 'uncommon', or 'rare'")
	try:
		with conn.cursor() as cur:
			cur.execute('''
				SELECT se.pt_name, dse.average_frequency
				FROM drug_side_effects dse
				JOIN side_effects se ON dse.side_effect_id = se.meddra_id
				WHERE dse.drug_id = %s AND dse.average_frequency > %s AND dse.average_frequency <= %s
				ORDER BY dse.average_frequency DESC
			''', (drug_id, freq_min, freq_max))
			results = cur.fetchall()
			for row in results:
				side_effects.append({
					'pt_name': row[0],
					'average_frequency': row[1]
				})
	except Exception as e:
		print(f"Error in get_sideeffects_by_rarity: {e}")
	finally:
		conn.close()
	return side_effects


def get_all_sideeffects_for_drug(drug_id):
	"""
	Returns all side effects for a given drug_id, regardless of rarity.
	Returns a list of dicts with 'pt_name' (side effect name) and 'average_frequency'.
	"""
	conn = get_connection()
	side_effects = []
	try:
		with conn.cursor() as cur:
			cur.execute('''
				SELECT se.pt_name, dse.average_frequency
				FROM drug_side_effects dse
				JOIN side_effects se ON dse.side_effect_id = se.meddra_id
				WHERE dse.drug_id = %s
				ORDER BY dse.average_frequency DESC
			''', (drug_id,))
			results = cur.fetchall()
			for row in results:
				side_effects.append({
					'pt_name': row[0],
					'average_frequency': row[1]
				})
	except Exception as e:
		print(f"Error in get_all_sideeffects_for_drug: {e}")
	finally:
		conn.close()
	return side_effects


def search_all_side_effects(search_term=''):
	"""
	Returns all side effects from the database, optionally filtered by search term.
	Returns a list of unique side effect names (pt_name).
	"""
	conn = get_connection()
	side_effects = []
	try:
		with conn.cursor() as cur:
			if search_term:
				# Search for side effects matching the search term
				cur.execute('''
					SELECT DISTINCT se.pt_name
					FROM side_effects se
					WHERE LOWER(se.pt_name) LIKE LOWER(%s)
					ORDER BY se.pt_name
					LIMIT 50
				''', (f'%{search_term}%',))
			else:
				# Get all side effects
				cur.execute('''
					SELECT DISTINCT se.pt_name
					FROM side_effects se
					ORDER BY se.pt_name
					LIMIT 50
				''')
			results = cur.fetchall()
			side_effects = [row[0] for row in results]
	except Exception as e:
		print(f"Error in search_all_side_effects: {e}")
	finally:
		conn.close()
	return side_effects


def get_side_effect_id_by_name(pt_name):
	"""
	Get the meddra_id for a side effect by its PT name.
	
	Args:
		pt_name: The PT name of the side effect
	
	Returns:
		meddra_id (int) if found, None otherwise
	"""
	conn = get_connection()
	meddra_id = None
	try:
		with conn.cursor() as cur:
			cur.execute('''
				SELECT meddra_id
				FROM side_effects
				WHERE LOWER(pt_name) = LOWER(%s)
				LIMIT 1
			''', (pt_name,))
			result = cur.fetchone()
			if result:
				meddra_id = result[0]
	except Exception as e:
		print(f"Error in get_side_effect_id_by_name: {e}")
	finally:
		conn.close()
	return meddra_id