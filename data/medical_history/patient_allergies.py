import streamlit as st
from db.database import get_connection


def get_patient_allergies(user_id):
    """Get all allergies for a patient."""
    conn = get_connection()
    allergies = []
    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT allergy_id, substance, reaction, severity, date_discovered, notes
                FROM patient_allergies
                WHERE user_id = %s
                ORDER BY severity DESC, created_at DESC
            ''', (user_id,))
            for row in cur.fetchall():
                # Map severity int to text
                severity_map = {1: 'MILD', 2: 'MODERATE', 3: 'CRITICAL'}
                allergies.append({
                    'id': row[0],
                    'substance': row[1],
                    'reaction': row[2],
                    'severity': severity_map.get(row[3], 'MODERATE'),
                    'date_discovered': row[4],
                    'notes': row[5]
                })
    except Exception as e:
        print(f"Error fetching patient allergies: {e}")
        st.session_state['db_fetch_error'] = str(e)
    finally:
        conn.close()
    return allergies


def insert_patient_allergy(user_id, substance, reaction, severity, date_discovered, notes=''):
    """Insert a new allergy."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Map severity text to int
            severity_map = {'MILD': 1, 'MODERATE': 2, 'CRITICAL': 3}
            severity_int = severity_map.get(severity, 2)
            
            cur.execute('''
                INSERT INTO patient_allergies (user_id, substance, reaction, severity, date_discovered, notes, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            ''', (user_id, substance, reaction, severity_int, date_discovered, notes))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error inserting patient allergy: {e}")
        st.session_state['db_insert_error'] = str(e)
        conn.rollback()
        return False
    finally:
        conn.close()


def delete_patient_allergy(allergy_id):
    """Delete an allergy."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM patient_allergies WHERE allergy_id = %s', (allergy_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting patient allergy: {e}")
        st.session_state['db_delete_error'] = str(e)
        conn.rollback()
        return False
    finally:
        conn.close()
