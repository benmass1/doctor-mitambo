itimport os
import google.generativeai as genai
from flask import Flask, render_template, redirect, url_for, session, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# --- INITIALIZATION ---
app = Flask(__name__)

# --- CONFIGURATION ---
app.secret_key = os.environ.get("SECRET_KEY", "DR_MITAMBO_PRO_SECURE_2026_V10")
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "mitambo_pro.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# --- GEMINI AI CONFIGURATION ---
# API Key mpya uliyotoa imewekwa hapa
API_KEY = "AIzaSyAswGa6VlXflWcPWRFyboki55RuI5LMV00"
genai.configure(api_key=API_KEY)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

# --- DATABASE MODELS ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    machines = db.relationship('Machine', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    serial = db.Column(db.String(50), unique=True)
    current_hours = db.Column(db.Integer, default=0)
    next_service_hours = db.Column(db.Integer, default=250)
    health_score = db.Column(db.Integer, default=100)
    last_service_date = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- DASHBOARD LOGIC ---
@app.route("/")
@app.route("/index")
@login_required
def index():
    fleet = Machine.query.filter_by(owner_id=current_user.id).all()
    total_fleet = len(fleet)
    needs_service = sum(1 for m in fleet if m.current_hours >= m.next_service_hours)
    
    avg_health = 0
    if total_fleet > 0:
        avg_health = sum(m.health_score for m in fleet) // total_fleet
        
    return render_template("index.html", 
                           user=current_user.username, 
                           fleet=fleet, 
                           fleet_count=total_fleet,
                           needs_service=needs_service,
                           avg_health=avg_health)
# --- AI DIAGNOSIS ENGINE ---
@app.route("/diagnosis", methods=["GET", "POST"])
@login_required
def diagnosis():
    result = None
    if request.method == "POST":
        query = request.form.get("error_code", "").strip()
        try:
            # Tunatumia jina fupi la model ili kuzuia kosa la 404
            model = genai.GenerativeModel('gemini-1.5-flash')

            prompt = (f"Wewe ni DR-MITAMBO PRO AI. Mteja ana tatizo hili: '{query}'. "
                      f"Chambua kitaalamu na utoe hatua za kurekebisha kwa Kiswahili.")
            
            response = model.generate_content(prompt)
            
            if response and response.text:
                result = response.text
            else:
                result = "AI imeshindwa kutoa jibu kwa sasa."
                
        except Exception as e:
            # Hii itakuonyesha kosa halisi kama bado kuna shida
            result = f"Hitilafu ya Kiufundi: AI haijaweza kuwasiliana. (Sababu: {str(e)})"
            
    return render_template("diagnosis.html", result=result)


# --- ROUTES ZA MODULI ZOTE ---
@app.route("/electrical")
@login_required
def electrical():
    return render_template("placeholder.html", title="Electrical Hub", icon="fa-bolt", desc="Michoro ya mifumo ya umeme.")

@app.route("/systems_op")
@login_required
def systems_op():
    return render_template("placeholder.html", title="Systems Operation", icon="fa-cogs", desc="Uelewa wa hydraulic na engine systems.")

@app.route("/troubleshooting")
@login_required
def troubleshooting():
    return render_template("placeholder.html", title="Troubleshooting Guide", icon="fa-wrench", desc="Mwongozo wa kutatua hitilafu.")

@app.route("/maintenance")
@login_required
def maintenance():
    data = Machine.query.filter_by(owner_id=current_user.id).all()
    return render_template("maintenance.html", machines=data)

@app.route("/calibration")
@login_required
def calibration():
    return render_template("placeholder.html", title="Calibration Tools", icon="fa-compass", desc="Kusawazisha sensorer na valves.")

@app.route("/harness")
@login_required
def harness():
    return render_template("placeholder.html", title="Harness Layout", icon="fa-network-wired", desc="Ramani za nyaya za mtambo.")

@app.route("/parts")
@login_required
def parts():
    return render_template("placeholder.html", title="Parts Book", icon="fa-search", desc="Katalogi ya vipuri asilia.")

@app.route("/manuals")
@login_required
def manuals():
    return render_template("placeholder.html", title="Service Manuals", icon="fa-book", desc="Maktaba ya vitabu vya ufundi.")

@app.route("/safety")
@login_required
def safety():
    return render_template("placeholder.html", title="Safety Standards", icon="fa-shield-halved", desc="Usalama kazini na HSE.")

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
            m = Machine(
                name=request.form.get("name"),
                brand=request.form.get("brand"),
                model=request.form.get("model"),
                serial=request.form.get("serial"),
                current_hours=int(request.form.get("hours", 0)),
                owner_id=current_user.id
            )
            db.session.add(m)
            db.session.commit()
            flash("Mtambo umeongezwa kikamilifu!", "success")
            return redirect(url_for("machines"))
        except Exception:
            db.session.rollback()
            flash("Hitilafu: Serial number tayari ipo.", "danger")
    return render_template("add_machine.html")

# --- AUTHENTICATION ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "POST":
        user = User.query.filter_by(username=request.form.get("username")).first()
        if user and user.check_password(request.form.get("password")):
            login_user(user)
            return redirect(url_for("index"))
        flash("Jina au Password si sahihi.", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u_name = request.form.get("username")
        if User.query.filter_by(username=u_name).first():
            flash("Jina hili tayari lipo.", "danger")
            return redirect(url_for("register"))
        u = User(username=u_name)
        u.set_password(request.form.get("password"))
        db.session.add(u)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.errorhandler(404)
def not_found(e):
    return render_template("placeholder.html", title="Not Found", icon="fa-circle-exclamation", desc="Ukurasa huu haupo."), 404

# --- DATABASE START ---
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
