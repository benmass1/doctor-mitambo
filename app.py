import os
from flask import Flask, render_template, redirect, url_for, session, request, flash

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "dr_mitambo_pro_ultra_secret"
)

# =========================
# DASHBOARD BUTTONS CONFIG
# =========================
buttons = [
    {'id': 'diag', 'title': 'AI Diagnosis', 'icon': 'fa-microchip', 'route': 'diagnosis', 'desc': 'CAT & Komatsu Experts'},
    {'id': 'elec', 'title': 'Electrical', 'icon': 'fa-bolt', 'route': 'electrical', 'desc': 'Wiring & Pinouts'},
    {'id': 'sys', 'title': 'Systems Op', 'icon': 'fa-cogs', 'route': 'systems_op', 'desc': 'Hydraulic & Engine Op'},
    {'id': 'trouble', 'title': 'Troubleshoot', 'icon': 'fa-wrench', 'route': 'troubleshooting', 'desc': 'Step-by-Step Guides'},
    {'id': 'serv', 'title': 'Service', 'icon': 'fa-calendar-check', 'route': 'maintenance', 'desc': 'Maintenance Logs'},
    {'id': 'man', 'title': 'Manuals', 'icon': 'fa-book', 'route': 'manuals', 'desc': 'Library ya Mitambo'},
    {'id': 'parts', 'title': 'Parts Book', 'icon': 'fa-search', 'route': 'parts', 'desc': 'Spare Parts Lookup'},
    {'id': 'calib', 'title': 'Calibration', 'icon': 'fa-sliders-h', 'route': 'calibration', 'desc': 'Sensor & Valve Calibration'},
    {'id': 'harness', 'title': 'Harness Hub', 'icon': 'fa-project-diagram', 'route': 'harness', 'desc': 'Connector Views'},
    {'id': 'safety', 'title': 'Safety Op', 'icon': 'fa-hard-hat', 'route': 'safety', 'desc': 'Operation Safety'}
]

# =========================
# AUTH ROUTES
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # LOGIN SIMPLE (baadaye utaweka DB)
        if username and password:
            session["logged_in"] = True
            session["user"] = username
            return redirect(url_for("index"))

        flash("Tafadhali jaza taarifa zote", "danger")

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
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return redirect(url_for("index"))


@app.route("/index")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    return render_template(
        "index.html",
        buttons=buttons,
        user=session.get("user")
    )

# =========================
# CORE MODULE ROUTES
# =========================
@app.route("/diagnosis")
def diagnosis():
    return secure_page("diagnosis.html")


@app.route("/electrical")
def electrical():
    return secure_page("electrical.html")


@app.route("/maintenance")
def maintenance():
    return secure_page("maintenance.html")


# =========================
# PLACEHOLDER MODULES
# =========================
@app.route("/systems_op")
def systems_op():
    return placeholder("Systems Operation")


@app.route("/troubleshooting")
def troubleshooting():
    return placeholder("Troubleshooting")


@app.route("/manuals")
def manuals():
    return placeholder("Manuals Library")


@app.route("/parts")
def parts():
    return placeholder("Parts Book")


@app.route("/calibration")
def calibration():
    return placeholder("Calibration")


@app.route("/harness")
def harness():
    return placeholder("Harness Hub")


@app.route("/safety")
def safety():
    return placeholder("Safety Operation")

# =========================
# HELPERS
# =========================
def secure_page(template):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template(template)


def placeholder(title):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("placeholder.html", title=title)

# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
