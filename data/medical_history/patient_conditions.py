import streamlit as st
from db.database import get_connection


def get_patient_conditions(user_id):
    """Get all medical conditions for a patient."""
    conn = get_connection()
    conditions = []
    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT condition_id, condition_name, severity, diagnosis_date, status, notes
                FROM patient_conditions
                WHERE user_id = %s
                ORDER BY created_at DESC
            ''', (user_id,))
            for row in cur.fetchall():
                conditions.append({
                    'id': row[0],
                    'name': row[1],
                    'severity': row[2],
                    'diagnosed_date': row[3],
                    'status': row[4],
                    'notes': row[5]
                })
    except Exception as e:
        print(f"Error fetching patient conditions: {e}")
        st.session_state['db_fetch_error'] = str(e)
    finally:
        conn.close()
    return conditions


def insert_patient_condition(user_id, condition_name, severity, diagnosis_date, status, notes=''):
    """Insert a new medical condition."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO patient_conditions (user_id, condition_name, severity, diagnosis_date, status, notes, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            ''', (user_id, condition_name, severity, diagnosis_date, status, notes))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error inserting patient condition: {e}")
        st.session_state['db_insert_error'] = str(e)
        conn.rollback()
        return False
    finally:
        conn.close()


def delete_patient_condition(condition_id):
    """Delete a medical condition."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM patient_conditions WHERE condition_id = %s', (condition_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting patient condition: {e}")
        st.session_state['db_delete_error'] = str(e)
        conn.rollback()
        return False
    finally:
        conn.close()
