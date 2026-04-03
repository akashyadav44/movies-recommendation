# 🎬 Movie Recommendation System

A content-based movie recommendation web app built with Python, Streamlit, and TMDB API — developed as a PBL (Project Based Learning) project.

---

## 🔗 Live Demo

👉 [Click here to open the app](https://your-app-link.streamlit.app)

---

## 📌 Features

- 🔍 **Smart Search** — Search movies by keyword with autocomplete suggestions
- 🎯 **TF-IDF Recommendations** — Content-based similarity using NLP
- 🎭 **Genre Recommendations** — Find similar movies by genre
- ⭐ **Ratings Display** — TMDB public ratings with visual bar
- 📊 **Similarity Score** — Shows how closely a movie matches (High / Medium / Low)
- 🤖 **AI Movie Chatbot** — Ask anything about movies (Powered by Groq Llama 3)
- 🔐 **User Authentication** — Login & Register system
- 📱 **Responsive UI** — Works on all screen sizes

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | FastAPI |
| ML Model | TF-IDF + Cosine Similarity |
| Database | TMDB API |
| AI Chatbot | Groq (Llama 3) |
| Deployment | Streamlit Cloud + Render |
| Language | Python 3.9+ |

---

## 🧠 How It Works

### Content-Based Filtering
1. Movie ke `overview`, `genres`, aur `tagline` ko combine karke `tags` banate hain
2. Text ko preprocess karte hain — lowercase, stopword removal, lemmatization
3. TF-IDF Vectorizer se har movie ka vector banate hain
4. Query movie aur baaki movies ke beech **Cosine Similarity** calculate karte hain
5. Top N similar movies return karte hain with similarity score

### Why Cosine Similarity?
- Vector magnitude se independent hoti hai
- Lambi aur choti movie descriptions equally compare hoti hain
- Score 0 to 1 ke beech hota hai — easy to interpret

---

## 📁 Project Structure

```
movies-recommendation/
│
├── app.py               # Streamlit frontend (main file)
├── main.py              # Alternative entry point
├── chatbot.py           # AI chatbot logic (Groq)
├── auth.py              # Login / Register logic
├── requirements.txt     # Python dependencies
│
├── .streamlit/
│   └── secrets.toml     # API keys (not pushed to GitHub)
│
└── README.md
```

---

## 🔑 API Keys Required

| Key | Where to get | Free? |
|-----|-------------|-------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | ✅ Yes |
| TMDB API | Handled by backend | ✅ Yes |

---

## 📊 Similarity Score Guide

| Score | Label | Meaning |
|-------|-------|---------|
| 70%+ | 🟢 High match | Very similar content |
| 40–70% | 🟡 Medium match | Somewhat similar |
| <40% | 🔵 Low match | Loosely related |

---

## ⚠️ Known Limitations

- Asymmetric recommendations — Movie A suggests B, but B may not suggest A (due to cosine ranking)
- No user personalization — same recommendations for all users
- Cold start — new movies not in dataset won't appear
- Spelling mistakes not handled in search

---

## 🚀 Future Improvements

- [ ] Collaborative Filtering (user ratings based)
- [ ] Watch History tracking
- [ ] Watchlist / Favourites
- [ ] Advanced Search (actor/director)
- [ ] Analytics Dashboard
- [ ] Smart Filter (sort by rating/genre/year)

---

## 👨‍💻 Developer

**Akash Yadav**
- GitHub: [@akashyadav44](https://github.com/akashyadav44)

---

## 📄 License

This project is built for educational purposes as part of a PBL assignment.
