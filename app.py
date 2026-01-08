import os
from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dr_mitambo_ultra_secure_key")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ================= MODELS =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, p): self.password_hash = generate_password_hash(p)
    def check_password(self, p): return check_password_hash(self.password_hash, p)

class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    serial = db.Column(db.String(50))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

# ================= AUTH =================
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        u,p = request.form["username"], request.form["password"]
        if User.query.filter_by(username=u).first():
            flash("User tayari yupo"); return redirect(url_for("register"))
        user = User(username=u); user.set_password(p)
        db.session.add(user); db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u,p = request.form["username"], request.form["password"]
        user = User.query.filter_by(username=u).first()
        if user and user.check_password(p):
            session["uid"]=user.id; session["user"]=user.username
            return redirect(url_for("index"))
        flash("Login imekataa")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ================= CORE =================
@app.route("/")
@app.route("/index")
def index():
    if not session.get("uid"): return redirect(url_for("login"))
    return render_template("index.html", user=session["user"])

# ================= MODULE ROUTES =================
@app.route("/diagnosis")       ;def diagnosis():       return secure("diagnosis.html")
@app.route("/electrical")      ;def electrical():      return secure("electrical.html")
@app.route("/systems_op")      ;def systems_op():      return secure("systems_op.html")
@app.route("/troubleshooting");def troubleshooting(): return secure("troubleshooting.html")
@app.route("/maintenance")     ;def maintenance():     return secure("maintenance.html")
@app.route("/manuals")         ;def manuals():         return secure("manuals.html")
@app.route("/parts")           ;def parts():           return secure("parts.html")
@app.route("/calibration")     ;def calibration():     return secure("calibration.html")
@app.route("/harness")         ;def harness():         return secure("harness.html")
@app.route("/safety")          ;def safety():          return secure("safety.html")

# ================= MACHINES =================
@app.route("/machines")
def machines():
    if not session.get("uid"): return redirect(url_for("login"))
    data = Machine.query.filter_by(owner_id=session["uid"]).all()
    return render_template("machines.html", machines=data)

@app.route("/add-machine", methods=["GET","POST"])
def add_machine():
    if request.method=="POST":
        m = Machine(
            name=request.form["name"],
            brand=request.form["brand"],
            model=request.form["model"],
            serial=request.form["serial"],
            owner_id=session["uid"]
        )
        db.session.add(m); db.session.commit()
        return redirect(url_for("machines"))
    return render_template("add_machine.html")

def secure(tpl):
    if not session.get("uid"): return redirect(url_for("login"))
    return render_template(tpl)

with app.app_context():
    db.create_all()

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",8000)))
