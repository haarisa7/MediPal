def get_drug_display_name(drug_id):
    from db.database import get_connection
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT display_name FROM drugs WHERE drug_id = %s', (drug_id,))
            row = cur.fetchone()
            if row:
                return row[0]
    except Exception:
        pass
    finally:
        conn.close()
    return f"Drug {drug_id}"
def get_drug_id_by_name(drug_name):
    """Return the drug_id for a given drug name (case-insensitive), or None if not found."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT drug_id FROM drugs WHERE display_name ILIKE %s LIMIT 1
            """,
            (drug_name,)
        )
        row = cur.fetchone()
        if row:
            return row[0]
        return None
    except Exception as e:
        print('get_drug_id_by_name error:', e)
        return None
    finally:
        cur.close()
        conn.close()
# Enhanced medication data with rich details and adherence tracking
from datetime import datetime, timedelta
import random
from db.database import get_connection

def get_drugs_by_search(query: str, limit: int = 10):
    """Search the `drugs` table for display_name ILIKE %query% and return list of dicts.

    Returns items like {'display_name': ..., 'drug_id': ...}.
    """
    if not query or not query.strip():
        return []

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT drug_id, display_name
            FROM drugs
            WHERE display_name ILIKE %s
            ORDER BY display_name
            LIMIT %s
            """,
            (f"%{query}%", limit)
        )
        rows = cur.fetchall()
        results = []
        for row in rows:
            drug_id, display_name = row
            results.append({'drug_id': drug_id, 'display_name': display_name})
        return results
    except Exception as e:
        print('get_drugs_by_search error:', e)
        return []
    finally:
        cur.close()
        conn.close()