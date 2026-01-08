import os
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

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

# --- MODELS (UBORESHAJI WA DATABASE) ---
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
    current_hours = db.Column(db.Integer, default=0) # Saa za sasa
    next_service_hours = db.Column(db.Integer, default=250) # Saa za service
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- AUTH ROUTES ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "POST":
        u, p = request.form.get("username"), request.form.get("password")
        if User.query.filter_by(username=u).first():
            flash("Jina hili tayari lipo.", "danger")
            return redirect(url_for("register"))
        new_user = User(username=u)
        new_user.set_password(p)
        db.session.add(new_user)
        db.session.commit()
        flash("Akaunti imetengenezwa!", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "POST":
        u, p = request.form.get("username"), request.form.get("password")
        user = User.query.filter_by(username=u).first()
        if user and user.check_password(p):
            login_user(user)
            return redirect(url_for("index"))
        flash("Login imefeli. Angalia jina au nywila.", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# --- DASHBOARD ---
@app.route("/")
@app.route("/index")
@login_required
def index():
    fleet_count = Machine.query.filter_by(owner_id=current_user.id).count()
    return render_template("index.html", user=current_user.username, fleet_count=fleet_count)

# --- AI DIAGNOSIS (UBONGO WA MFUMO) ---
@app.route("/diagnosis", methods=["GET", "POST"])
@login_required
def diagnosis():
    result = None
    if request.method == "POST":
        code = request.form.get("error_code", "").upper().strip()
        solutions = {
            # Caterpillar
            "102-3": "CAT Boost Pressure Sensor: Voltage iko juu. Kagua sensor na nyaya.",
            "110-3": "CAT Engine Coolant Temp: Joto la maji limezidi. Kagua radiator na sensor.",
            "190-8": "CAT Engine Speed Signal: Signal siyo ya kawaida. Kagua Speed sensor kwenye flywheel.",
            # Komatsu
            "E11": "Komatsu Engine Overload: Punguza mzigo wa kazi, mtambo unalemewa.",
            "E15": "Komatsu Water Temp High: Joto la maji limezidi kiwango.",
            "CA441": "Komatsu Battery Voltage Low: Chaji ya betri iko chini sana. Kagua alternator.",
            # Sinotruk
            "P0087": "Sinotruk Fuel Rail Pressure Low: Shinikizo la mafuta ni dogo. Kagua fuel filter.",
            "P0299": "Sinotruk Turbo Underboost: Turbo haitoi shinikizo la kutosha.",
            # General
            "P0101": "MAF Sensor: Hitilafu ya mzunguko wa hewa. Safisha air filter.",
            "HYD-LOW": "Low Hydraulic Oil: Ongeza mafuta ya hydraulic mara moja."
        }
        result = solutions.get(code, f"Code '{code}' haijapatikana. Wasiliana na mtaalamu wa Dr. Mitambo.")
    return render_template("diagnosis.html", result=result)

# --- MODULI NYINGINE (ZINAZOTUMIA PLACEHOLDER KWA SASA) ---
@app.route("/electrical")
@login_required
def electrical():
    return render_template("placeholder.html", title="Electrical System")

@app.route("/systems_op")
@login_required
def systems_op():
    return render_template("placeholder.html", title="Systems Operation")

@app.route("/troubleshooting")
@login_required
def troubleshooting():
    return render_template("placeholder.html", title="Troubleshooting")

@app.route("/maintenance")
@login_required
def maintenance():
    user_machines = Machine.query.filter_by(owner_id=current_user.id).all()
    return render_template("placeholder.html", title="Maintenance Schedule", machines=user_machines)

@app.route("/manuals")
@login_required
def manuals():
    return render_template("placeholder.html", title="Service Manuals")

@app.route("/parts")
@login_required
def parts():
    return render_template("placeholder.html", title="Parts Book")

@app.route("/calibration")
@login_required
def calibration():
    return render_template("placeholder.html", title="Calibration Tools")

@app.route("/harness")
@login_required
def harness():
    return render_template("placeholder.html", title="Wiring Harness")

@app.route("/safety")
@login_required
def safety():
    return render_template("placeholder.html", title="Safety Standards")

# --- MACHINE MANAGEMENT ---
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
                current_hours=request.form.get("hours", 0),
                owner_id=current_user.id
            )
            db.session.add(m); db.session.commit()
            flash("Mashine imeongezwa!", "success")
            return redirect(url_for("machines"))
        except:
            db.session.rollback()
            flash("Hitilafu: Serial number inaweza kuwa tayari ipo.", "danger")
    return render_template("add_machine.html")

# --- INITIALIZATION ---
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
