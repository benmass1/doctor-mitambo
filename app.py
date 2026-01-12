hereimport os
import json
import io
import base64
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

# --- AI INTEGRATION (GROQ PEKEE KWA USALAMA) ---
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

# --- ANZA GROQ CLIENT (Pamoja na kurekebisha kosa la proxies) ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
groq_client = None

if Groq and httpx and GROQ_API_KEY:
    try:
        # Tunalazimisha httpx kutotumia proxies kuzuia hitilafu ya Python 3.13
        custom_http_client = httpx.Client(trust_env=False)
        groq_client = Groq(
            api_key=GROQ_API_KEY,
            http_client=custom_http_client
        )
        print("Groq Client imewaka vizuri!")
    except Exception as e:
        print(f"Bado kuna shida ya Groq: {e}")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
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
    id = db.Column(# ... (kama awali)
        db.Integer, primary_key=True)
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
# ROUTES
# =====================================================
@app.route("/")
@app.route("/index")
@login_required
def index():
    fleet = Machine.query.filter_by(owner_id=current_user.id).all()
    total_fleet = len(fleet)
    needs_service = sum(1 for m in fleet if m.current_hours >= m.next_service_hours)
    avg_health = (sum(m.health_score for m in fleet) // total_fleet if total_fleet > 0 else 0)
    return render_template("index.html", user=current_user.username, fleet=fleet, fleet_count=total_fleet, needs_service=needs_service, avg_health=avg_health)

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

@app.route("/systems_op")
@login_required
def systems_op(): return render_template("systems_op.html")

@app.route("/troubleshooting")
@login_required
def troubleshooting(): return render_template("troubleshooting.html")

@app.route("/parts")
@login_required
def parts(): return render_template("parts.html")

# --- Placeholder Routes ---
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
@app.route("/schematics")
@login_required
def schematics(): return render_template("placeholder.html", title="Schematics", icon="fa-project-diagram")
@app.route("/reports")
@login_required
def reports(): return render_template("placeholder.html", title="Reports", icon="fa-chart-line")
@app.route("/alerts")
@login_required
def alerts(): return render_template("placeholder.html", title="Alerts", icon="fa-bell")
@app.route("/settings")
@login_required
def settings(): return render_template("placeholder.html", title="Settings", icon="fa-cog")

# =====================================================
# AI SCAN & CHAT (MABORESHO YA GROQ VISION & LOGIC)
# =====================================================
@app.route("/api/scan-nameplate", methods=["POST"])
@login_required
def api_scan_nameplate():
    if 'image' not in request.files or not groq_client:
        return jsonify({"error": "Picha haijapatikana au Groq haijawaka."})
    
    try:
        file = request.files['image']
        # Geuza picha kuwa Base64 kwa ajili ya Groq Vision
        image_base64 = base64.b64encode(file.read()).decode('utf-8')
        
        # Tumia model ya Vision (Llama 3.2)
        response = groq_client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract machine brand, model, and serial number from this nameplate. Output as raw JSON only."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                        }
                    ]
                }
            ],
            temperature=0.1
        )
        
        # Kusafisha maandishi na kurudisha JSON
        res_text = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
        return jsonify(json.loads(res_text))
    except Exception as e:
        return jsonify({"error": f"Hitilafu ya Vision: {str(e)}"}), 500

@app.route("/api/ask_expert", methods=["POST"])
@login_required
def api_ask_expert():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip() or data.get("message", "").strip()
    category = data.get("category", "Diagnosis").strip()

    if not groq_client:
        return jsonify({"result": "Msaidizi hayupo kwa sasa."})

    try:
        # MAREKEBISHO: Tumia llama-3.3-70b na Temperature ndogo kwa usahihi
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": f"Wewe ni Dr. Mitambo Pro, mtaalamu wa ufundi Tanzania. Unasaidia kwenye kitengo cha {category}. Jibu maswali ya kiufundi pekee kwa Kiswahili fasaha na kwa usahihi wa 100%."
                },
                {"role": "user", "content": query}
            ],
            temperature=0.2, # Hii inazuia AI kutoa majibu yasiyohusiana
        )
        return jsonify({"result": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"result": f"Kosa la AI: {str(e)}"}), 200

# =====================================================
# AUTH & MANAGEMENT
# =====================================================
@app.route("/machines")
@login_required
def machines():
    data = Machine.query.filter_by(owner_id=current_user.id).all()
    return render_template("machines.html", machines=data)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = User.query.filter_by(username=request.form.get("username")).first()
        if u and u.check_password(request.form.get("password")):
            login_user(u); return redirect(url_for("index"))
        flash("Username au password si sahihi", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        if User.query.filter_by(username=username).first():
            flash("Username tayari ipo", "danger")
            return redirect(url_for("register"))
        u = User(username=username)
        u.set_password(request.form.get("password"))
        db.session.add(u); db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user(); return redirect(url_for("login"))

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
