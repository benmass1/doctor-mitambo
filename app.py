import os
import google.generativeai as genai
from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# --- CONFIGURATION ---
app.secret_key = os.environ.get("SECRET_KEY", "dr_mitambo_super_secret_key_2026")
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "mitambo.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# --- GEMINI AI CONFIGURATION ---
API_KEY = "AIzaSyCt3qnEOM3CXBIbtd5aIW_p-qS4iFShh7Q"
genai.configure(api_key=API_KEY)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# --- DATABASE MODELS ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
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
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- CORE ROUTES ---
@app.route("/")
@app.route("/index")
@login_required
def index():
    fleet = Machine.query.filter_by(owner_id=current_user.id).all()
    return render_template("index.html", user=current_user.username, fleet=fleet, fleet_count=len(fleet))

@app.route("/diagnosis", methods=["GET", "POST"])
@login_required
def diagnosis():
    result = None
    if request.method == "POST":
        query = request.form.get("error_code", "").strip()
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Wewe ni DR-MITAMBO AI. Mteja anauliza: '{query}'. Jibu kitaalamu kwa Kiswahili."
            response = model.generate_content(prompt)
            result = response.text
        except:
            result = "Hitilafu: AI imeshindwa kuunganishwa."
    return render_template("diagnosis.html", result=result)

# --- MODULI ZILIZOBAKI (SASA ZIPO ZOTE) ---

@app.route("/electrical")
@login_required
def electrical(): 
    return render_template("placeholder.html", title="Electrical Hub", icon="fa-bolt")

@app.route("/systems_op")
@login_required
def systems_op(): 
    return render_template("placeholder.html", title="Systems Operation", icon="fa-cogs")

@app.route("/troubleshooting")
@login_required
def troubleshooting(): 
    return render_template("placeholder.html", title="Troubleshooting Guide", icon="fa-wrench")

@app.route("/maintenance")
@login_required
def maintenance():
    data = Machine.query.filter_by(owner_id=current_user.id).all()
    return render_template("maintenance.html", machines=data)

@app.route("/calibration") # <--- IMEONGEZWA
@login_required
def calibration(): 
    return render_template("placeholder.html", title="Sensor Calibration", icon="fa-compass")

@app.route("/safety") # <--- IMEONGEZWA
@login_required
def safety(): 
    return render_template("placeholder.html", title="Safety & Regulations", icon="fa-shield-halved")

@app.route("/parts")
@login_required
def parts(): 
    return render_template("placeholder.html", title="Parts Book", icon="fa-search")

@app.route("/manuals")
@login_required
def manuals(): 
    return render_template("placeholder.html", title="Service Manuals", icon="fa-book")

@app.route("/machines")
@login_required
def machines():
    data = Machine.query.filter_by(owner_id=current_user.id).all()
    return render_template("machines.html", machines=data)

@app.route("/add-machine", methods=["GET", "POST"])
@login_required
def add_machine():
    if request.method == "POST":
        m = Machine(name=request.form.get("name"), brand=request.form.get("brand"),
                    model=request.form.get("model"), serial=request.form.get("serial"),
                    current_hours=int(request.form.get("hours", 0)), owner_id=current_user.id)
        db.session.add(m); db.session.commit()
        return redirect(url_for("machines"))
    return render_template("add_machine.html")

# --- AUTH ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form.get("username")).first()
        if user and user.check_password(request.form.get("password")):
            login_user(user); return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = User(username=request.form.get("username"))
        u.set_password(request.form.get("password"))
        db.session.add(u); db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
