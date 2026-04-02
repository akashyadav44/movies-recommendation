from auth import login_user, register_user
from chatbot import render_chatbot_sidebar   # ← NEW

import os
import time
import requests
import streamlit as st
from typing import Optional

# =============================
# CONFIG
# =============================
API_BASE = os.getenv("API_BASE", "https://movie-rec-466x.onrender.com")
API_BASE = "https://movie-rec-466x.onrender.com" or "http://127.0.0.1:8000"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# =============================
# LOGIN / REGISTER PAGE
# =============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def show_login_page():
    st.markdown("""
    <div style='text-align:center; padding: 40px 0 10px 0;'>
        <h1>🎬 Movie Recommender</h1>
        <p style='color:#6b7280;'>Login to get personalized recommendations</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

        with tab1:
            st.markdown("### Welcome Back!")
            email = st.text_input("Email", placeholder="enter your email", key="login_email")
            password = st.text_input("Password", type="password", placeholder="enter your password", key="login_pass")

            if st.button("Login", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please fill all fields!")
                else:
                    success, result = login_user(email, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = result
                        st.success(f"Welcome back {result}! 🎉")
                        st.rerun()
                    else:
                        st.error(result)

        with tab2:
            st.markdown("### Create Account")
            new_username = st.text_input("Username", placeholder="enter username", key="reg_user")
            new_email = st.text_input("Email", placeholder="enter email", key="reg_email")
            new_password = st.text_input("Password", type="password", placeholder="min 6 characters", key="reg_pass")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="repeat password", key="reg_confirm")

            if st.button("Register", use_container_width=True, type="primary"):
                if not all([new_username, new_email, new_password, confirm_password]):
                    st.error("Please fill all fields!")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters!")
                elif new_password != confirm_password:
                    st.error("Passwords do not match!")
                else:
                    success, msg = register_user(new_username, new_email, new_password)
                    if success:
                        st.success("Account created! Please login. ✅")
                    else:
                        st.error(msg)

# =============================
# ROUTING — Login check
# =============================
if not st.session_state.logged_in:
    show_login_page()
    st.stop()

# =============================
# STYLES
# =============================
st.markdown("""
<style>
.block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1400px; }
.small-muted { color:#6b7280; font-size: 0.92rem; }
.movie-title { font-size: 0.9rem; line-height: 1.15rem; height: 2.3rem; overflow: hidden; }
.card { border: 1px solid rgba(0,0,0,0.08); border-radius: 16px; padding: 14px; background: rgba(255,255,255,0.7); }
.rating-bar-bg { background: #e5e7eb; border-radius: 4px; height: 4px; margin: 3px 0 4px 0; }
.sim-label-high  { color: #16a34a; font-size: 0.72rem; font-weight: 600; }
.sim-label-mid   { color: #d97706; font-size: 0.72rem; font-weight: 600; }
.sim-label-low   { color: #3b82f6; font-size: 0.72rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# =============================
# STATE + ROUTING
# =============================
if "view" not in st.session_state:
    st.session_state.view = "home"
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None
if "current_movie_title" not in st.session_state:
    st.session_state.current_movie_title = None

qp_view = st.query_params.get("view")
qp_id   = st.query_params.get("id")
if qp_view in ("home", "details"):
    st.session_state.view = qp_view
if qp_id:
    try:
        st.session_state.selected_tmdb_id = int(qp_id)
        st.session_state.view = "details"
    except:
        pass


def goto_home():
    st.session_state.view = "home"
    st.session_state.current_movie_title = None
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()


def goto_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()


# =============================
# API HELPERS
# =============================
@st.cache_data(ttl=60)
def api_get_json(path: str, params: Optional[dict] = None):
    for attempt in range(3):
        try:
            r = requests.get(f"{API_BASE}{path}", params=params, timeout=60)
            if r.status_code >= 400:
                return None, f"HTTP {r.status_code}: {r.text[:300]}"
            return r.json(), None
        except requests.exceptions.Timeout:
            if attempt < 2:
                time.sleep(3)
                continue
            return None, "⏳ Server waking up... please refresh in 30 seconds"
        except Exception as e:
            return None, f"Request failed: {e}"


# =============================
# POSTER GRID — WITH RATING + SIMILARITY
# =============================
def poster_grid(cards, cols=6, key_prefix="grid"):
    if not cards:
        st.info("No movies to show.")
        return

    rows = (len(cards) + cols - 1) // cols
    idx = 0
    for r in range(rows):
        colset = st.columns(cols)
        for c in range(cols):
            if idx >= len(cards):
                break
            m = cards[idx]
            idx += 1

            tmdb_id = m.get("tmdb_id")
            title   = m.get("title", "Untitled")
            poster  = m.get("poster_url")
            rating  = m.get("vote_average")
            sim     = m.get("similarity_score")

            with colset[c]:
                if poster:
                    st.image(poster, use_container_width=True)
                else:
                    st.write("🖼️ No poster")

                if rating:
                    try:
                        r_val = float(rating)
                        stars = "⭐" * round(r_val / 2)
                        st.markdown(
                            f"<div style='font-size:0.75rem;color:#f59e0b;margin:2px 0'>"
                            f"{stars} <b>{r_val:.1f}</b>/10</div>",
                            unsafe_allow_html=True
                        )
                        bar_pct = int((r_val / 10) * 100)
                        st.markdown(
                            f"<div class='rating-bar-bg'>"
                            f"<div style='width:{bar_pct}%;background:#f59e0b;height:4px;border-radius:4px'></div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    except:
                        pass

                if sim is not None:
                    try:
                        pct = round(float(sim) * 100)
                        if pct >= 70:
                            css_class, icon, label = "sim-label-high", "▮▮▮", "High match"
                        elif pct >= 40:
                            css_class, icon, label = "sim-label-mid",  "▮▮░", "Medium match"
                        else:
                            css_class, icon, label = "sim-label-low",  "▮░░", "Low match"
                        st.markdown(
                            f"<div class='{css_class}'>{icon} {pct}% — {label}</div>",
                            unsafe_allow_html=True
                        )
                    except:
                        pass

                if st.button("Open", key=f"{key_prefix}_{r}_{c}_{idx}_{tmdb_id}"):
                    if tmdb_id:
                        goto_details(tmdb_id)

                st.markdown(
                    f"<div class='movie-title'>{title}</div>",
                    unsafe_allow_html=True
                )


# =============================
# TFIDF ITEMS → CARDS
# =============================
def to_cards_from_tfidf_items(tfidf_items):
    cards = []
    for x in tfidf_items or []:
        tmdb = x.get("tmdb") or {}
        if tmdb.get("tmdb_id"):
            cards.append({
                "tmdb_id":          tmdb["tmdb_id"],
                "title":            tmdb.get("title") or x.get("title") or "Untitled",
                "poster_url":       tmdb.get("poster_url"),
                "vote_average":     tmdb.get("vote_average") or x.get("vote_average"),
                "similarity_score": x.get("similarity_score") or x.get("score"),
            })
    return cards


# =============================
# TMDB SEARCH PARSER
# =============================
def parse_tmdb_search_to_cards(data, keyword: str, limit: int = 24):
    keyword_l = keyword.strip().lower()

    if isinstance(data, dict) and "results" in data:
        raw = data.get("results") or []
        raw_items = []
        for m in raw:
            title = (m.get("title") or "").strip()
            tmdb_id = m.get("id")
            poster_path = m.get("poster_path")
            if not title or not tmdb_id:
                continue
            raw_items.append({
                "tmdb_id":      int(tmdb_id),
                "title":        title,
                "poster_url":   f"{TMDB_IMG}{poster_path}" if poster_path else None,
                "vote_average": m.get("vote_average"),
                "release_date": m.get("release_date", ""),
            })

    elif isinstance(data, list):
        raw_items = []
        for m in data:
            tmdb_id = m.get("tmdb_id") or m.get("id")
            title   = (m.get("title") or "").strip()
            if not title or not tmdb_id:
                continue
            raw_items.append({
                "tmdb_id":      int(tmdb_id),
                "title":        title,
                "poster_url":   m.get("poster_url"),
                "vote_average": m.get("vote_average"),
                "release_date": m.get("release_date", ""),
            })
    else:
        return [], []

    matched    = [x for x in raw_items if keyword_l in x["title"].lower()]
    final_list = matched if matched else raw_items

    suggestions = []
    for x in final_list[:10]:
        year  = (x.get("release_date") or "")[:4]
        label = f"{x['title']} ({year})" if year else x["title"]
        suggestions.append((label, x["tmdb_id"]))

    cards = [{
        "tmdb_id":      x["tmdb_id"],
        "title":        x["title"],
        "poster_url":   x["poster_url"],
        "vote_average": x.get("vote_average"),
    } for x in final_list[:limit]]

    return suggestions, cards


# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.markdown("## 🎬 Menu")
    st.markdown(f"👤 **{st.session_state.username}**")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username  = ""
        st.rerun()
    st.markdown("---")
    if st.button("🏠 Home"):
        goto_home()
    st.markdown("---")
    st.markdown("### 🏠 Home Feed")
    home_category = st.selectbox(
        "Category",
        ["trending", "popular", "top_rated", "now_playing", "upcoming"],
        index=0,
    )
    grid_cols = st.slider("Grid columns", 4, 8, 6)

    st.markdown("---")
    st.markdown("### 📊 Similarity Guide")
    st.markdown("🟢 **▮▮▮ 70%+** — High match")
    st.markdown("🟡 **▮▮░ 40–70%** — Medium match")
    st.markdown("🔵 **▮░░ <40%** — Low match")
    st.markdown("⭐ **Rating** — TMDB public score")

# ← AI Chatbot — sidebar mein render karo, current movie context ke saath
render_chatbot_sidebar(
    current_movie=st.session_state.get("current_movie_title")
)

# =============================
# HEADER
# =============================
st.title("🎬 Movie Recommender")
st.markdown(
    "<div class='small-muted'>Type keyword → dropdown suggestions + matching results → open → details + recommendations</div>",
    unsafe_allow_html=True,
)
st.divider()

# ==========================================================
# VIEW: HOME
# ==========================================================
if st.session_state.view == "home":
    typed = st.text_input(
        "Search by movie title (keyword)", placeholder="Type: avenger, batman, love..."
    )
    st.divider()

    if typed.strip():
        if len(typed.strip()) < 2:
            st.caption("Type at least 2 characters for suggestions.")
        else:
            data, err = api_get_json("/tmdb/search", params={"query": typed.strip()})

            if err or data is None:
                st.error(f"Search failed: {err}")
            else:
                suggestions, cards = parse_tmdb_search_to_cards(data, typed.strip(), limit=24)

                if suggestions:
                    labels   = ["-- Select a movie --"] + [s[0] for s in suggestions]
                    selected = st.selectbox("Suggestions", labels, index=0)
                    if selected != "-- Select a movie --":
                        label_to_id = {s[0]: s[1] for s in suggestions}
                        goto_details(label_to_id[selected])
                else:
                    st.info("No suggestions found. Try another keyword.")

                st.markdown("### Results")
                poster_grid(cards, cols=grid_cols, key_prefix="search_results")
        st.stop()

    st.markdown(f"### 🏠 Home — {home_category.replace('_',' ').title()}")
    home_cards, err = api_get_json("/home", params={"category": home_category, "limit": 24})
    if err or not home_cards:
        st.error(f"Home feed failed: {err or 'Unknown error'}")
        st.stop()

    poster_grid(home_cards, cols=grid_cols, key_prefix="home_feed")

# ==========================================================
# VIEW: DETAILS
# ==========================================================
elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.warning("No movie selected.")
        if st.button("← Back to Home"):
            goto_home()
        st.stop()

    a, b = st.columns([3, 1])
    with a:
        st.markdown("### 📄 Movie Details")
    with b:
        if st.button("← Back to Home"):
            goto_home()

    data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        st.stop()

    # Chatbot ko current movie ka context do
    st.session_state.current_movie_title = data.get("title", "")

    left, right = st.columns([1, 2.4], gap="large")

    with left:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        if data.get("poster_url"):
            st.image(data["poster_url"], use_container_width=True)
        else:
            st.write("🖼️ No poster")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"## {data.get('title','')}")
        release = data.get("release_date") or "-"
        genres  = ", ".join([g["name"] for g in data.get("genres", [])]) or "-"
        rating  = data.get("vote_average")

        st.markdown(f"<div class='small-muted'>Release: {release}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='small-muted'>Genres: {genres}</div>",   unsafe_allow_html=True)

        if rating:
            try:
                r_val = float(rating)
                stars = "⭐" * round(r_val / 2)
                st.markdown(
                    f"<div style='margin:8px 0;font-size:1rem;color:#f59e0b'>"
                    f"{stars} <b>{r_val:.1f} / 10</b> &nbsp;"
                    f"<span style='color:#6b7280;font-size:0.85rem'>(TMDB Rating)</span></div>",
                    unsafe_allow_html=True
                )
                bar_pct = int((r_val / 10) * 100)
                st.markdown(
                    f"<div class='rating-bar-bg'>"
                    f"<div style='width:{bar_pct}%;background:#f59e0b;height:6px;border-radius:4px'></div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            except:
                pass

        st.markdown("---")
        st.markdown("### Overview")
        st.write(data.get("overview") or "No overview available.")
        st.markdown("</div>", unsafe_allow_html=True)

    if data.get("backdrop_url"):
        st.markdown("#### Backdrop")
        st.image(data["backdrop_url"], use_container_width=True)

    st.divider()
    st.markdown("### ✅ Recommendations")

    title = (data.get("title") or "").strip()
    if title:
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": title, "tfidf_top_n": 12, "genre_limit": 12},
        )

        if not err2 and bundle:
            tfidf_cards = to_cards_from_tfidf_items(bundle.get("tfidf_recommendations"))
            st.markdown("#### 🔎 Similar Movies (TF-IDF)")
            st.caption("Similarity % = kitna content match karta hai | ⭐ = TMDB public rating")
            poster_grid(tfidf_cards, cols=grid_cols, key_prefix="details_tfidf")

            st.markdown("#### 🎭 More Like This (Genre)")
            poster_grid(bundle.get("genre_recommendations", []), cols=grid_cols, key_prefix="details_genre")

        else:
            st.info("Showing Genre recommendations (fallback).")
            genre_only, err3 = api_get_json("/recommend/genre", params={"tmdb_id": tmdb_id, "limit": 18})
            if not err3 and genre_only:
                poster_grid(genre_only, cols=grid_cols, key_prefix="details_genre_fallback")
            else:
                st.warning("No recommendations available right now.")
    else:
        st.warning("No title available to compute recommendations.")