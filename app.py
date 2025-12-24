from flask import Flask, render_template, request, redirect, url_for, session
import feedparser, sqlite3
from bs4 import BeautifulSoup   # For cleaning summaries
from sentiment import get_sentiment  # Custom sentiment module
from datetime import datetime   # 👈 Added for year

# ---------------- Flask App ----------------
app = Flask(__name__)
app.secret_key = "super_secret_key"

NEWS_URL = "https://news.google.com/news/rss"
DB_NAME = "users.db"

# ---------------- Database Setup ----------------
def init_db():
    """Initialize the SQLite database for storing users."""
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE,
                      password TEXT)''')
        conn.commit()

def check_user(username, password):
    """Check if user exists with matching credentials."""
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        return c.fetchone()

def add_user(username, password):
    """Add a new user into the database."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# ---------------- Utility Functions ----------------
def clean_html(raw_html):
    """Remove HTML tags from news summaries."""
    return BeautifulSoup(raw_html, "html.parser").get_text()

def fetch_news():
    feed = feedparser.parse(NEWS_URL)
    articles = []
    for entry in feed.entries[:20]:
        summary = clean_html(entry.get("description", ""))
        score, sentiment = get_sentiment(entry.title + " " + summary)
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "summary": summary,
            "score": round(score, 2),     # ✅ will now show VADER score
            "sentiment": sentiment
        })
    return articles

def calculate_overall_sentiment(articles):
    """Calculate overall sentiment score and label."""
    if not articles:
        return 0, "Neutral"

    avg_score = sum(a["score"] for a in articles) / len(articles)

    if avg_score >= 1:
        sentiment = "Positive"
    elif avg_score == 0:
        sentiment = "Neutral"
    else:
        sentiment = "Negative"

    return round(avg_score, 2), sentiment

# ---------------- Routes ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    """Handle user login & registration."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if "register" in request.form:
            if add_user(username, password):
                return redirect(url_for("login"))
            else:
                return render_template("login.html", error="User already exists!")

        elif "login" in request.form:
            if check_user(username, password):
                session["user"] = username
                return redirect(url_for("news"))
            else:
                return render_template("login.html", error="Invalid username or password!")

    return render_template("login.html")

@app.route("/news")
def news():
    """Display news with sentiment analysis."""
    if "user" not in session:
        return redirect(url_for("login"))

    articles = fetch_news()
    overall_score, overall_sentiment = calculate_overall_sentiment(articles)

    return render_template(
        "news.html",
        articles=articles,
        overall=overall_sentiment,
        overall_score=overall_score,
        year=datetime.now().year   # 👈 Added here
    )

@app.route("/logout")
def logout():
    """Logout user and clear session."""
    session.pop("user", None)
    return redirect(url_for("login"))

# ---------------- Run App ----------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
