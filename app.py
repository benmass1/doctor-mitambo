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

# --- MODELS ---
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
    # Mpya: Saa za matengenezo
    current_hours = db.Column(db.Integer, default=0)
    next_service_hours = db.Column(db.Integer, default=250)
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
        u = request.form.get("username")
        p = request.form.get("password")
        if User.query.filter_by(username=u).first():
            flash("Jina hili tayari lipo.", "danger")
            return redirect(url_for("register"))
        new_user = User(username=u)
        new_user.set_password(p)
        db.session.add(new_user)
        db.session.commit()
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
        flash("Kuingia kumeshindikana.", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# --- DASHBOARD & MODULE ROUTES ---
@app.route("/")
@app.route("/index")
@login_required
def index():
    return render_template("index.html", user=current_user.username)

@app.route("/diagnosis", methods=["GET", "POST"])
@login_required
def diagnosis():
    result = None
    if request.method == "POST":
        code = request.form.get("error_code", "").upper()
        solutions = {
            "P0101": "MAF Sensor: Kagua filter ya hewa na nyaya za sensor.",
            "E001": "Overheating: Kagua kiwango cha coolant na feni ya redieta.",
            "HYD-05": "Low Hydraulic Pressure: Kagua kiwango cha mafuta na pampu."
        }
        result = solutions.get(code, "Code haitambuliki bado kwenye mfumo.")
    return render_template("placeholder.html", title="AI Diagnosis", result=result)

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
    # Hapa tunaweza kuweka logic ya kuonyesha list ya mashine na masaa
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
            db.session.add(m)
            db.session.commit()
            flash("Mashine imeongezwa!", "success")
            return redirect(url_for("machines"))
        except:
            db.session.rollback()
            flash("Hitilafu imetokea.", "danger")
    return render_template("add_machine.html")

# --- INITIALIZATION ---
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
