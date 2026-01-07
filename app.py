import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "dr_mitambo_key_2026"

# Configuration kwa ajili ya Uploads
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Fake Database kwa ajili ya majaribio
fleet_data = [
    {"model": "CAT 336D", "sn": "MBD0254", "type": "Excavator", "status": "Operational", "hours": "4250"},
    {"model": "D8R", "sn": "9EM0124", "type": "Bulldozer", "status": "Breakdown", "hours": "8900"}
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/diagnosis')
def diagnosis():
    return render_template('diagnosis.html')

@app.route('/maintenance')
def maintenance():
    return render_template('maintenance.html', fleet=fleet_data)

@app.route('/add_machine', methods=['POST'])
def add_machine():
    if request.method == 'POST':
        new_machine = {
            "model": request.form.get('model'),
            "sn": request.form.get('serial'),
            "type": request.form.get('type'),
            "status": request.form.get('status'),
            "hours": request.form.get('hours')
        }
        fleet_data.append(new_machine)
    return redirect(url_for('maintenance'))

@app.route('/electrical', methods=['GET', 'POST'])
def electrical():
    filename = None
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return render_template('electrical.html', uploaded_file=filename)

if __name__ == '__main__':
    # Muhimu kwa Koyeb kusoma Port
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
