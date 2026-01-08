import os
from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# =========================
# APP CONFIG
# =========================
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dr_mitambo_pro_ultra_secret")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================
# DATABASE MODELS
# =========================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    serial = db.Column(db.String(50))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

# =========================
# DASHBOARD BUTTONS
# =========================
buttons = [
    {'title': 'AI Diagnosis', 'icon': 'fa-microchip', 'route': 'diagnosis'},
    {'title': 'Electrical', 'icon': 'fa-bolt', 'route': 'electrical'},
    {'title': 'Systems Op', 'icon': 'fa-cogs', 'route': 'systems_op'},
    {'title': 'Troubleshoot', 'icon': 'fa-wrench', 'route': 'troubleshooting'},
    {'title': 'Service', 'icon': 'fa-calendar-check', 'route': 'maintenance'},
    {'title': 'Manuals', 'icon': 'fa-book', 'route': 'manuals'},
    {'title': 'Parts Book', 'icon': 'fa-search', 'route': 'parts'},
    {'title': 'Calibration', 'icon': 'fa-sliders-h', 'route': 'calibration'},
    {'title': 'Machines', 'icon': 'fa-tractor', 'route': 'machines'}
]

# =========================
# AUTH ROUTES
# =========================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Jaza taarifa zote", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(username=username).first():
            flash("Mtumiaji tayari yupo", "warning")
            return redirect(url_for("register"))

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Usajili umefanikiwa, tafadhali login", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session["logged_in"] = True
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("index"))

        flash("Username au password sio sahihi", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# =========================
# HOME & DASHBOARD
# =========================
@app.route("/")
def home():
    return redirect(url_for("index"))


@app.route("/index")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    return render_template(
        "index.html",
        buttons=buttons,
        user=session.get("username")
    )

# =========================
# MACHINES MODULE
# =========================
@app.route("/machines")
def machines():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user_machines = Machine.query.filter_by(owner_id=session["user_id"]).all()
    return render_template("machines.html", machines=user_machines)


@app.route("/add-machine", methods=["GET", "POST"])
def add_machine():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if request.method == "POST":
        machine = Machine(
            name=request.form.get("name"),
            brand=request.form.get("brand"),
            model=request.form.get("model"),
            serial=request.form.get("serial"),
            owner_id=session["user_id"]
        )
        db.session.add(machine)
        db.session.commit()

        flash("Mashine imeongezwa kikamilifu", "success")
        return redirect(url_for("machines"))

    return render_template("add_machine.html")

# =========================
# PLACEHOLDER ROUTES
# =========================
@app.route("/diagnosis")
def diagnosis(): return placeholder("AI Diagnosis")

@app.route("/electrical")
def electrical(): return placeholder("Electrical")

@app.route("/systems_op")
def systems_op(): return placeholder("Systems Operation")

@app.route("/troubleshooting")
def troubleshooting(): return placeholder("Troubleshooting")

@app.route("/maintenance")
def maintenance(): return placeholder("Maintenance")

@app.route("/manuals")
def manuals(): return placeholder("Manuals")

@app.route("/parts")
def parts(): return placeholder("Parts Book")

@app.route("/calibration")
def calibration(): return placeholder("Calibration")

def placeholder(title):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("placeholder.html", title=title)

# =========================
# INIT DB
# =========================
with app.app_context():
    db.create_all()

# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
