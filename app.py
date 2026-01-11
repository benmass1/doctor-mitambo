import os
import json
import io
from datetime import datetime

from flask import (
    Flask, render_template, redirect, url_for,
    request, flash, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user,
    login_required, logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

# --- GROQ & HTTPX INTEGRATION ---
try:
    from groq import Groq
    import httpx
except ImportError:
    Groq = None
    httpx = None

# =====================================================
# APP INITIALIZATION
# =====================================================
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "DR_MITAMBO_PRO_SECURE_2026_V10")

# --- ANZA GROQ CLIENT (Fixed kwa mazingira ya Seva) ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
groq_client = None

if Groq and GROQ_API_KEY:
    try:
        # Tunatengeneza mteja wa HTTP bila proxies ili kuzuia hitilafu
        custom_http_client = httpx.Client()
        groq_client = Groq(
            api_key=GROQ_API_KEY,
            http_client=custom_http_client
        )
    except Exception as e:
        print(f"Hakuweza kuanzisha Groq Client: {e}")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Muhimu kwa SQLite: Tumia '////' kwa absolute path ili kuzuia makosa ya mazingira ya Linux (Koyeb)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////" + os.path.join(BASE_DIR, "mitambo_pro.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# =====================================================
# DATABASE MODELS
# =====================================================
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    machines = db.relationship("Machine", backref="owner", lazy=True, cascade="all, delete")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Machine(db.Model):
    __tablename__ = "machines"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    serial = db.Column(db.String(50), unique=True, nullable=False)
    current_hours = db.Column(db.Integer, default=0)
    next_service_hours = db.Column(db.Integer, default=250)
    health_score = db.Column(db.Integer, default=100)
    last_service_date = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# =====================================================
# CORE ROUTES
# =====================================================
@app.route("/")
@app.route("/index")
@login_required
def index():
    fleet = Machine.query.filter_by(owner_id=current_user.id).all()
    total_fleet = len(fleet)
    needs_service = sum(1 for m in fleet if m.current_hours >= m.next_service_hours)
    avg_health = (sum(m.health_score for m in fleet) // total_fleet if total_fleet > 0 else 0)
    return render_template("index.html", 
                         user=current_user.username, 
                         fleet=fleet, 
                         fleet_count=total_fleet, 
                         needs_service=needs_service, 
                         avg_health=avg_health)

@app.route("/diagnosis")
@login_required
def diagnosis(): return render_template("diagnosis.html")

@app.route("/electrical")
@login_required
def electrical(): return render_template("electrical.html")

@app.route("/maintenance")
@login_required
def maintenance():
    machines = Machine.query.filter_by(owner_id=current_user.id).all()
    return render_template("maintenance.html", machines=machines)

# =====================================================
# AI CONTEXTUAL ASSISTANT (Fixed for reliability)
# =====================================================
@app.route("/api/ask_expert", methods=["POST"])
@login_required
def api_ask_expert():
    # Tunahakikisha JSON inasomwa vizuri bila kujali jina la ufunguo (query au message)
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip() or data.get("message", "").strip()
    category = data.get("category", "Ufundi").strip()

    if not query:
        return jsonify({"result": "Tafadhali andika swali lako."})

    if not groq_client:
        return jsonify({"result": "AI haijasanidiwa. Weka GROQ_API_KEY kule Koyeb."})

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": f"Wewe ni Dr. Mitambo Pro, mtaalamu wa ufundi Tanzania. Unasaidia kwenye {category}. Jibu kwa Kiswahili fasaha na ufafanuzi mfupi."
                },
                {"role": "user", "content": query}
            ],
            temperature=0.5,
        )
        return jsonify({"result": response.choices[0].message.content})
    except Exception as e:
        # Inatoa kosa fupi badala ya 500 crash
        return jsonify({"result": f"Hitilafu: {str(e)}"}), 200

# =====================================================
# AUTHENTICATION
# =====================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = User.query.filter_by(username=request.form.get("username")).first()
        if u and u.check_password(request.form.get("password")):
            login_user(u)
            return redirect(url_for("index"))
        flash("Jina au Password si sahihi.", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if User.query.filter_by(username=username).first():
            flash("Username tayari ipo.", "danger")
            return redirect(url_for("register"))
        u = User(username=username)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        flash("Akaunti imeumbwa!", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# Hii inatengeneza database mara ya kwanza
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # Tumia PORT inayotolewa na Koyeb au 8000 kama default
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
