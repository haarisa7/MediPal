from db.database import get_connection


def _build_report_dict(row, include_rarity=False):
    """Build a report dict from a database row."""
    base_dict = {
        'report_id': row[0],
        'user_id': row[1],
        'patient_med_id': row[2],
        'side_effect_id': row[3],
        'severity': row[4],
        'notes': row[5],
        'reported_at': row[6],
        'side_effect_name': row[7],
        'display_name': row[8],
        'dose': row[9],
        'resolved': row[10]
    }
    
    if include_rarity and len(row) > 10:
        # Determine rarity based on frequency (row[10] when fetching with frequency)
        frequency = row[10]
        if frequency is not None:
            if frequency > 0.5:
                rarity = 'common'
            elif frequency > 0.2:
                rarity = 'uncommon'
            else:
                rarity = 'rare'
        else:
            rarity = 'unknown'
        
        base_dict.update({
            'reported_at': row[6].strftime('%Y-%m-%d') if row[6] else 'Unknown date',
            'rarity': rarity,
            'frequency': frequency
        })
    
    return base_dict


def _execute_report_query(query, params, single=False, include_rarity=False):
    """Execute a query and return report dict(s)."""
    conn = get_connection()
    result = None if single else []
    
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            
            if single:
                row = cur.fetchone()
                if row:
                    result = _build_report_dict(row, include_rarity)
            else:
                results = cur.fetchall()
                result = [_build_report_dict(row, include_rarity) for row in results]
    except Exception as e:
        print(f"Error executing report query: {e}")
    finally:
        conn.close()
    
    return result


# Base query for fetching reports
_BASE_REPORT_QUERY = '''
    SELECT 
        pse.report_id,
        pse.user_id,
        pse.patient_med_id,
        pse.side_effect_id,
        pse.severity,
        pse.notes,
        pse.reported_at,
        se.pt_name as side_effect_name,
        d.display_name,
        pm.dose,
        pse.resolved
    FROM patient_side_effects pse
    LEFT JOIN side_effects se ON pse.side_effect_id = se.meddra_id
    LEFT JOIN patient_medications pm ON pse.patient_med_id = pm.patient_med_id
    LEFT JOIN drugs d ON pm.drug_id = d.drug_id
'''


def insert_side_effect_report(user_id, side_effect_id, severity, notes, patient_med_id=None):
    """
    Insert a new side effect report into the patient_side_effects table.
    
    Args:
        user_id: Patient's user ID
        side_effect_id: MedDRA PT ID for the side effect
        severity: Severity rating (1-5)
        notes: User's description/notes
        patient_med_id: Optional - ID from patient_meds table
    
    Returns:
        report_id of the newly inserted report, or None if failed
    """
    conn = get_connection()
    report_id = None
    
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO patient_side_effects 
                (user_id, patient_med_id, side_effect_id, severity, notes)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING report_id
            ''', (user_id, patient_med_id, side_effect_id, severity, notes))
            
            result = cur.fetchone()
            if result:
                report_id = result[0]
            
            conn.commit()
    except Exception as e:
        print(f"Error inserting side effect report: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    return report_id


def get_patient_side_effect_reports(user_id):
    """Get all side effect reports for a patient."""
    query = _BASE_REPORT_QUERY + '''
        WHERE pse.user_id = %s
        ORDER BY pse.reported_at DESC
    '''
    return _execute_report_query(query, (user_id,))


def get_patient_side_effect_report_by_id(report_id):
    """Get a single side effect report by its ID."""
    query = _BASE_REPORT_QUERY + 'WHERE pse.report_id = %s'
    return _execute_report_query(query, (report_id,), single=True)


def get_active_patient_side_effect_reports(user_id):
    """Get all active (unresolved) side effect reports for a patient."""
    query = _BASE_REPORT_QUERY + '''
        WHERE pse.user_id = %s AND (pse.resolved = FALSE OR pse.resolved IS NULL)
        ORDER BY pse.reported_at DESC
    '''
    return _execute_report_query(query, (user_id,))


def get_resolved_patient_side_effect_reports(user_id):
    """Get all resolved side effect reports for a patient."""
    query = _BASE_REPORT_QUERY + '''
        WHERE pse.user_id = %s AND pse.resolved = TRUE
        ORDER BY pse.reported_at DESC
    '''
    return _execute_report_query(query, (user_id,))


def resolve_side_effect_report(report_id):
    """
    Mark a side effect report as resolved.
    """
    conn = get_connection()
    
    try:
        with conn.cursor() as cur:
            cur.execute('''
                UPDATE patient_side_effects
                SET resolved = TRUE
                WHERE report_id = %s
            ''', (report_id,))
            
            conn.commit()
            return True
    except Exception as e:
        print(f"Error resolving side effect report: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_recent_patient_side_effect_reports(user_id, limit=3):
    """Get recent side effect reports for a patient (limited to most recent)."""
    query = '''
        SELECT 
            pse.report_id,
            pse.user_id,
            pse.patient_med_id,
            pse.side_effect_id,
            pse.severity,
            pse.notes,
            pse.reported_at,
            se.pt_name as side_effect_name,
            d.display_name,
            pm.dose,
            dse.average_frequency
        FROM patient_side_effects pse
        LEFT JOIN side_effects se ON pse.side_effect_id = se.meddra_id
        LEFT JOIN patient_medications pm ON pse.patient_med_id = pm.patient_med_id
        LEFT JOIN drugs d ON pm.drug_id = d.drug_id
        LEFT JOIN drug_side_effects dse ON (dse.drug_id = d.drug_id AND dse.side_effect_id = se.meddra_id)
        WHERE pse.user_id = %s
        ORDER BY pse.reported_at DESC
        LIMIT %s
    '''
    return _execute_report_query(query, (user_id, limit), include_rarity=True)


def get_side_effect_reports_count(user_id):
    """
    Get total count of side effect reports for a patient.
    
    Args:
        user_id: Patient's user ID
    
    Returns:
        Integer count of total reports.
    """
    conn = get_connection()
    count = 0
    
    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT COUNT(*) 
                FROM patient_side_effects 
                WHERE user_id = %s
            ''', (user_id,))
            
            result = cur.fetchone()
            if result:
                count = result[0]
    except Exception as e:
        print(f"Error fetching side effect reports count: {e}")
    finally:
        conn.close()
    
    return count


def get_patient_side_effect_analytics(user_id):
    """
    Get analytics for patient's side effect reports.
    
    Args:
        user_id: Patient's user ID
    
    Returns:
        Dict with analytics: total_reports, active_reports, healthcare_notified, severe_reports
    """
    conn = get_connection()
    analytics = {
        'total_reports': 0,
        'active_reports': 0,
        'medications_affected': 0,
        'severe_reports': 0
    }
    
    try:
        with conn.cursor() as cur:
            # Total reports count
            cur.execute('''
                SELECT COUNT(*) 
                FROM patient_side_effects 
                WHERE user_id = %s
            ''', (user_id,))
            result = cur.fetchone()
            if result:
                analytics['total_reports'] = result[0]
            
            # Active reports (unresolved)
            cur.execute('''
                SELECT COUNT(*) 
                FROM patient_side_effects 
                WHERE user_id = %s AND (resolved = FALSE OR resolved IS NULL)
            ''', (user_id,))
            result = cur.fetchone()
            if result:
                analytics['active_reports'] = result[0]
            
            # Medications affected (count distinct medications with reports)
            cur.execute('''
                SELECT COUNT(DISTINCT pm.drug_id)
                FROM patient_side_effects pse
                INNER JOIN patient_medications pm ON pse.patient_med_id = pm.patient_med_id
                WHERE pse.user_id = %s
            ''', (user_id,))
            result = cur.fetchone()
            if result:
                analytics['medications_affected'] = result[0]
            
            # Severe reports (rare side effects - frequency <= 0.2)
            cur.execute('''
                SELECT COUNT(*)
                FROM patient_side_effects pse
                LEFT JOIN patient_medications pm ON pse.patient_med_id = pm.patient_med_id
                LEFT JOIN drugs d ON pm.drug_id = d.drug_id
                LEFT JOIN drug_side_effects dse ON (dse.drug_id = d.drug_id AND dse.side_effect_id = pse.side_effect_id)
                WHERE pse.user_id = %s AND dse.average_frequency <= 0.2
            ''', (user_id,))
            result = cur.fetchone()
            if result:
                analytics['severe_reports'] = result[0]
            
    except Exception as e:
        print(f"Error fetching side effect analytics: {e}")
    finally:
        conn.close()
    
    return analytics
