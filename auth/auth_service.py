import bcrypt
from db.database import get_connection

def register_user(email: str, password: str, role: int) -> bool:
    hashed_pw = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO users (email, password, role)
            VALUES (%s, %s, %s)
            """,
            (email, hashed_pw, role)
        )
        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        print(e)
        return False

    finally:
        cur.close()
        conn.close()


def login_user(email: str, password: str):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT user_id, password, role
            FROM users
            WHERE email = %s
            """,
            (email,)
        )
        user = cur.fetchone()

        if user is None:
            return None

        user_id, stored_hash, role = user

        if bcrypt.checkpw(
            password.encode("utf-8"),
            stored_hash.encode("utf-8")
        ):
            return {
                "user_id": user_id,
                "email": email,
                "role": role
            }

        return None

    finally:
        cur.close()
        conn.close()


def get_user_by_email(email: str):
    """Return user dict for given email, or None."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT user_id, email, role
            FROM users
            WHERE email = %s
            """,
            (email,)
        )
        row = cur.fetchone()
        if row is None:
            return None
        user_id, email, role = row
        return {"user_id": user_id, "email": email, "role": role}
    finally:
        cur.close()
        conn.close()


def get_user_by_id(user_id: int):
    """Return user dict for given user_id, or None."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT user_id, email, role
            FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        )
        row = cur.fetchone()
        if row is None:
            return None
        user_id, email, role = row
        return {"user_id": user_id, "email": email, "role": role}
    finally:
        cur.close()
        conn.close()


def update_user_email(user_id: int, new_email: str) -> bool:
    """Update the email for a user. Returns True on success."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE users
            SET email = %s
            WHERE user_id = %s
            """,
            (new_email, user_id)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("update_user_email error:", e)
        return False
    finally:
        cur.close()
        conn.close()


def change_user_password(user_identifier, old_password: str, new_password: str) -> bool:
    """Change the user's password.

    `user_identifier` may be a user_id (int) or email (str).
    Returns True on success, False on failure (wrong current password or DB error).
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        if isinstance(user_identifier, int):
            cur.execute("SELECT password FROM users WHERE user_id = %s", (user_identifier,))
        else:
            cur.execute("SELECT password FROM users WHERE email = %s", (user_identifier,))

        row = cur.fetchone()
        if row is None:
            return False

        stored_hash = row[0]
        if not bcrypt.checkpw(old_password.encode('utf-8'), stored_hash.encode('utf-8')):
            return False

        new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        if isinstance(user_identifier, int):
            cur.execute("UPDATE users SET password = %s WHERE user_id = %s", (new_hash, user_identifier))
        else:
            cur.execute("UPDATE users SET password = %s WHERE email = %s", (new_hash, user_identifier))

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        print("change_user_password error:", e)
        return False

    finally:
        cur.close()
        conn.close()