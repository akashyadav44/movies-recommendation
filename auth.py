import bcrypt
import os

# =============================
# SUPABASE SETUP
# =============================
try:
    from supabase import create_client

    # Streamlit Cloud pe secrets se lo
    try:
        import streamlit as st
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
        SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    except:
        # Local ke liye .env se lo
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except:
            pass
        SUPABASE_URL = os.getenv("SUPABASE_URL", "")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise Exception("Keys not found!")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    SUPABASE_OK = True
    print("Supabase connected!")

except Exception as e:
    SUPABASE_OK = False
    print(f"Supabase connection failed: {e}")


# =============================
# REGISTER USER
# =============================
def register_user(username: str, email: str, password: str):
    if not SUPABASE_OK:
        return False, "Database not connected!"
    try:
        hashed = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        supabase.table("users").insert({
            "username": username,
            "email": email,
            "password": hashed
        }).execute()

        return True, "Registration successful!"

    except Exception as e:
        if "duplicate" in str(e).lower():
            return False, "Username or Email already exists!"
        return False, f"Error: {e}"


# =============================
# LOGIN USER
# =============================
def login_user(email: str, password: str):
    if not SUPABASE_OK:
        return False, "Database not connected!"
    try:
        result = supabase.table("users")\
            .select("username, password")\
            .eq("email", email)\
            .execute()

        if not result.data:
            return False, "Email not found!"

        user = result.data[0]

        if bcrypt.checkpw(
            password.encode("utf-8"),
            user["password"].encode("utf-8")
        ):
            return True, user["username"]
        else:
            return False, "Wrong password!"

    except Exception as e:
        return False, f"Error: {e}"


# =============================
# DUMMY init_db
# =============================
def init_db():
    pass