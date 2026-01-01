import streamlit as st
from db.database import get_connection


def get_emergency_contacts(user_id):
    """Get all emergency contacts for a patient."""
    conn = get_connection()
    contacts = []
    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT contact_id, name, relationship, phone, email, contact_type
                FROM patient_emergency_contacts
                WHERE user_id = %s
                ORDER BY contact_type, created_at DESC
            ''', (user_id,))
            for row in cur.fetchall():
                contacts.append({
                    'id': row[0],
                    'name': row[1],
                    'relation': row[2],
                    'phone': row[3],
                    'email': row[4],
                    'type': row[5]
                })
    except Exception as e:
        print(f"Error fetching emergency contacts: {e}")
        st.session_state['db_fetch_error'] = str(e)
    finally:
        conn.close()
    return contacts


def insert_emergency_contact(user_id, name, relationship, phone, contact_type, email=''):
    """Insert a new emergency contact."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO patient_emergency_contacts (user_id, name, relationship, phone, email, contact_type, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            ''', (user_id, name, relationship, phone, email, contact_type))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error inserting emergency contact: {e}")
        st.session_state['db_insert_error'] = str(e)
        conn.rollback()
        return False
    finally:
        conn.close()


def delete_emergency_contact(contact_id):
    """Delete an emergency contact."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM patient_emergency_contacts WHERE contact_id = %s', (contact_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting emergency contact: {e}")
        st.session_state['db_delete_error'] = str(e)
        conn.rollback()
        return False
    finally:
        conn.close()
