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

# --- GROQ & HTTPX INTEGRATION (REFIXED) ---
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

# --- ANZA GROQ CLIENT (Kurekebisha TypeError: proxies) ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
groq_client = None

if Groq and httpx and GROQ_API_KEY:
    try:
        # Tunatengeneza mteja wa HTTP bila proxies ili kuzuia hitilafu kwenye Python 3.13
        custom_http_client = httpx.Client(proxies=None)
        groq_client = Groq(
            api_key=GROQ_API_KEY,
            http_client=custom_http_client
        )
    except Exception as e:
        print(f"Hakuweza kuanzisha Groq Client: {e}")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "mitambo_pro.db")
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
# CORE ROUTES (DASHBOARD)
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

# =====================================================
# MODULE ROUTES
# =====================================================
@app.route("/diagnosis")
@login_required
def diagnosis(): return render_template("diagnosis.html")

@app.route("/electrical")
@login_required
def electrical(): return render_template("electrical.html")

@app.route("/systems_op")
@login_required
def systems_op(): return render_template("systems_op.html")

@app.route("/troubleshooting")
@login_required
def troubleshooting(): return render_template("troubleshooting.html")

@app.route("/parts")
@login_required
def parts(): return render_template("parts.html")

@app.route("/maintenance")
@login_required
def maintenance():
    machines = Machine.query.filter_by(owner_id=current_user.id).all()
    return render_template("maintenance.html", machines=machines)

@app.route("/manuals")
@login_required
def manuals(): return render_template("placeholder.html", title="Manuals", icon="fa-book-open")

@app.route("/safety")
@login_required
def safety(): return render_template("placeholder.html", title="Safety", icon="fa-hard-hat")

@app.route("/calibration")
@login_required
def calibration(): return render_template("placeholder.html", title="Calibration", icon="fa-sliders-h")

@app.route("/harness")
@login_required
def harness(): return render_template("placeholder.html", title="Harness Layout", icon="fa-network-wired")

# =====================================================
# NYONGEZA: ROUTES 5 NA SCAN API
# =====================================================

@app.route("/api/scan-nameplate", methods=["POST"])
@login_required
def api_scan_nameplate():
    return jsonify({"error": "Vision API bado inahitaji usanidi wa Model ya Picha"})

@app.route("/schematics")
@login_required
def schematics():
    return render_template("placeholder.html", title="Schematics", icon="fa-project-diagram", desc="Wiring & Hydraulic diagrams library.")

@app.route("/reports")
@login_required
def reports():
    return render_template("placeholder.html", title="Reports", icon="fa-chart-line", desc="Detailed machine productivity reports.")

@app.route("/alerts")
@login_required
def alerts():
    return render_template("placeholder.html", title="Alerts", icon="fa-bell", desc="Active fault codes and warnings.")

@app.route("/settings")
@login_required
def settings():
    return render_template("placeholder.html", title="Settings", icon="fa-cog", desc="User profile and system configuration.")

# =====================================================
# AI CONTEXTUAL ASSISTANT (IMEUNGANISHWA NA GROQ)
# =====================================================
@app.route("/api/ask_expert", methods=["POST"])
@login_required
def api_ask_expert():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip() or data.get("message", "").strip()
    category = data.get("category", "Diagnosis").strip()

    if not groq_client:
        return jsonify({"result": "Msaidizi wa AI hayupo kwa sasa. Hakikisha GROQ_API_KEY imewekwa Koyeb."})

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": f"Wewe ni Dr. Mitambo Pro, mtaalamu wa ufundi Tanzania. Unasaidia kwenye {category}. Jibu kwa Kiswahili fasaha."
                },
                {"role": "user", "content": query}
            ],
            temperature=0.6,
        )
        return jsonify({"result": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"result": f"Kosa la kiufundi: {str(e)}"}), 500

# =====================================================
# MACHINE MANAGEMENT & AUTH
# =====================================================
@app.route("/machines")
@login_required
def machines():
    data = Machine.query.filter_by(owner_id=current_user.id).all()
    return render_template("machines.html", machines=data)

@app.route("/add-machine", methods=["GET", "POST"])
@login_required
def add_machine():
    if request.method == "POST":
        try:
            brand = request.form.get("brand")
            model = request.form.get("model")
            m = Machine(
                name=f"{brand} {model}",
                brand=brand,
                model=model,
                serial=request.form.get("serial"),
                current_hours=int(request.form.get("hours", 0)),
                owner_id=current_user.id
            )
            db.session.add(m); db.session.commit()
            flash("Mtambo umeongezwa!", "success")
            return redirect(url_for("machines"))
        except: 
            db.session.rollback()
            flash("Serial tayari ipo.", "danger")
    return render_template("add_machine.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = User.query.filter_by(username=request.form.get("username")).first()
        if u and u.check_password(request.form.get("password")):
            login_user(u); return redirect(url_for("index"))
        flash("Jina au Password si sahihi.", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = User(username=request.form.get("username"))
        u.set_password(request.form.get("password"))
        db.session.add(u); db.session.commit()
        flash("Akaunti imeumbwa!", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user(); return redirect(url_for("login"))

@app.errorhandler(404)
def not_found(e): return render_template("placeholder.html", title="Not Found", icon="fa-exclamation-circle"), 404

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
