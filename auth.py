import sqlite3
import bcrypt
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")

# =============================
# DATABASE SETUP
# =============================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# =============================
# REGISTER USER
# =============================
def register_user(username: str, email: str, password: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Password hash karo
        hashed = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        c.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed.decode("utf-8"))
        )
        conn.commit()
        conn.close()
        return True, "Registration successful!"

    except sqlite3.IntegrityError:
        return False, "Username or Email already exists!"
    except Exception as e:
        return False, f"Error: {e}"

# =============================
# LOGIN USER
# =============================
def login_user(email: str, password: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute(
            "SELECT username, password FROM users WHERE email = ?",
            (email,)
        )
        row = c.fetchone()
        conn.close()

        if not row:
            return False, "Email not found!"

        username, hashed = row

        # Password verify karo
        if bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8")):
            return True, username
        else:
            return False, "Wrong password!"

    except Exception as e:
        return False, f"Error: {e}"