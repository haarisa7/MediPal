"""Data layer for medical events."""
from db.database import get_connection


def get_medical_events(user_id):
    """Get all medical events for a user, ordered by date descending."""
    conn = get_connection()
    if not conn:
        print("Failed to get database connection")
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT event_id, user_id, event_type, event_name, event_description,
                   event_date, location, doctor_name, status, notes, success, created_at
            FROM patient_medical_events
            WHERE user_id = %s
            ORDER BY event_date DESC
        """, (user_id,))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        events = []
        for row in rows:
            events.append({
                'event_id': row[0],
                'user_id': row[1],
                'event_type': row[2],
                'event_name': row[3],
                'event_description': row[4],
                'event_date': row[5],
                'location': row[6],
                'doctor_name': row[7],
                'status': row[8],
                'notes': row[9],
                'success': row[10],
                'created_at': row[11]
            })
        
        return events
    except Exception as e:
        print(f"Error fetching medical events: {e}")
        return []


def get_event_counts(user_id):
    """Get counts of different event types for a user."""
    conn = get_connection()

    try:
        cursor = conn.cursor()
        
        # Total events
        cursor.execute("SELECT COUNT(*) FROM patient_medical_events WHERE user_id = %s", (user_id,))
        total = cursor.fetchone()[0]
        
        # Procedures
        cursor.execute("SELECT COUNT(*) FROM patient_medical_events WHERE user_id = %s AND event_type = 'Procedure'", (user_id,))
        procedures = cursor.fetchone()[0]
        
        # Hospital stays
        cursor.execute("SELECT COUNT(*) FROM patient_medical_events WHERE user_id = %s AND event_type = 'Hospital Stay'", (user_id,))
        hospital_stays = cursor.fetchone()[0]
        
        # Successful events
        cursor.execute("SELECT COUNT(*) FROM patient_medical_events WHERE user_id = %s AND success = TRUE", (user_id,))
        successful = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            'total': total,
            'procedures': procedures,
            'hospital_stays': hospital_stays,
            'success': successful
        }
    except Exception as e:
        print(f"Error fetching event counts: {e}")
        return {'total': 0, 'procedures': 0, 'hospital_stays': 0, 'success': 0}


def insert_medical_event(user_id, event_type, event_name, event_description, event_date, 
                         location, doctor_name, status, notes, success):
    """Insert a new medical event."""
    conn = get_connection()
    if not conn:
        print("Failed to get database connection")
        import streamlit as st
        st.session_state['db_insert_error'] = "Failed to connect to database"
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO patient_medical_events 
            (user_id, event_type, event_name, event_description, event_date, 
             location, doctor_name, status, notes, success, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (user_id, event_type, event_name, event_description, event_date, 
              location, doctor_name, status, notes, success))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error inserting medical event: {e}")
        import streamlit as st
        st.session_state['db_insert_error'] = str(e)
        conn.rollback()
        conn.close()
        return False


def delete_medical_event(event_id, user_id):
    """Delete a medical event (with user_id check for security)."""
    conn = get_connection()
    if not conn:
        print("Failed to get database connection")
        import streamlit as st
        st.session_state['db_delete_error'] = "Failed to connect to database"
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM patient_medical_events 
            WHERE event_id = %s AND user_id = %s
        """, (event_id, user_id))
        
        conn.commit()
        deleted = cursor.rowcount > 0
        cursor.close()
        conn.close()
        
        if not deleted:
            import streamlit as st
            st.session_state['db_delete_error'] = "Event not found or already deleted"
        
        return deleted
    except Exception as e:
        print(f"Error deleting medical event: {e}")
        import streamlit as st
        st.session_state['db_delete_error'] = str(e)
        conn.rollback()
        conn.close()
        return False


def update_medical_event(event_id, user_id, event_type, event_name, event_description, 
                        event_date, location, doctor_name, status, notes, success):
    """Update an existing medical event."""
    conn = get_connection()
    if not conn:
        print("Failed to get database connection")
        import streamlit as st
        st.session_state['db_update_error'] = "Failed to connect to database"
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE patient_medical_events 
            SET event_type = %s,
                event_name = %s,
                event_description = %s,
                event_date = %s,
                location = %s,
                doctor_name = %s,
                status = %s,
                notes = %s,
                success = %s
            WHERE event_id = %s AND user_id = %s
        """, (event_type, event_name, event_description, event_date, location, 
              doctor_name, status, notes, success, event_id, user_id))
        
        conn.commit()
        updated = cursor.rowcount > 0
        cursor.close()
        conn.close()
        
        if not updated:
            import streamlit as st
            st.session_state['db_update_error'] = "Event not found or no changes made"
        
        return updated
    except Exception as e:
        print(f"Error updating medical event: {e}")
        import streamlit as st
        st.session_state['db_update_error'] = str(e)
        conn.rollback()
        conn.close()
        return False


def get_date_range(user_id):
    """Get the earliest and latest event dates for a user."""
    conn = get_connection()
    if not conn:
        print("Failed to get database connection")
        return None, None
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MIN(event_date), MAX(event_date)
            FROM patient_medical_events
            WHERE user_id = %s
        """, (user_id,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return row[0], row[1]
    except Exception as e:
        print(f"Error fetching date range: {e}")
        return None, None
