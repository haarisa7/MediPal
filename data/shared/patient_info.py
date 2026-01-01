import streamlit as st
from db.database import get_connection


def get_patient_info(user_id):
    """Get patient info (blood type, weight, height)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT blood_type, weight_kg, height_cm, notes
                FROM patient_info
                WHERE user_id = %s
            ''', (user_id,))
            row = cur.fetchone()
            if row:
                return {
                    'blood_type': row[0],
                    'weight_kg': row[1],
                    'height_cm': row[2],
                    'notes': row[3]
                }
    except Exception as e:
        print(f"Error fetching patient info: {e}")
        st.session_state['db_fetch_error'] = str(e)
    finally:
        conn.close()
    return None


def upsert_patient_info(user_id, blood_type, weight_kg, height_cm, notes=''):
    """Insert or update patient info."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Check if record exists
            cur.execute('SELECT 1 FROM patient_info WHERE user_id = %s', (user_id,))
            exists = cur.fetchone()
            
            if exists:
                # Update existing record
                cur.execute('''
                    UPDATE patient_info
                    SET blood_type = %s, weight_kg = %s, height_cm = %s, notes = %s, updated_at = NOW()
                    WHERE user_id = %s
                ''', (blood_type, weight_kg, height_cm, notes, user_id))
            else:
                # Insert new record
                cur.execute('''
                    INSERT INTO patient_info (user_id, blood_type, weight_kg, height_cm, notes, updated_at)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                ''', (user_id, blood_type, weight_kg, height_cm, notes))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error upserting patient info: {e}")
        st.session_state['db_insert_error'] = str(e)
        conn.rollback()
        return False
    finally:
        conn.close()
