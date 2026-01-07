import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret_doctor_mitambo_key"

# FEATURE 1: Configuration ya Folder la Uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Hakikisha folder lipo
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# FEATURE 2: Database ya Muda (In-Memory Database) 
# Baadaye tutaweka SQL, kwa sasa tunatumia List ya Python
fleet_data = [
    {"id": 1, "model": "CAT 336D", "sn": "MBD0254", "type": "Excavator", "status": "Operational", "hours": 4250},
    {"id": 2, "model": "D8R", "sn": "9EM0124", "type": "Bulldozer", "status": "Breakdown", "hours": 8900}
]

# FEATURE 3: Helper function ya kuhakikisha faili ni sahihi
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# FEATURE 4: Dashboard Route
@app.route('/')
def index():
    return render_template('index.html', total=len(fleet_data))

# FEATURE 5: Diagnosis AI Backend Route
@app.route('/diagnosis')
def diagnosis():
    return render_template('diagnosis.html')

# FEATURE 6: Maintenance Route (Kusoma Data)
@app.route('/maintenance')
def maintenance():
    return render_template('maintenance.html', fleet=fleet_data)

# FEATURE 7: Add Machine Backend (Post Request)
@app.route('/add_machine', methods=['POST'])
def add_machine():
    new_machine = {
        "id": len(fleet_data) + 1,
        "model": request.form.get('model'),
        "sn": request.form.get('serial'),
        "type": request.form.get('type'),
        "status": request.form.get('status'),
        "hours": request.form.get('hours')
    }
    fleet_data.append(new_machine)
    flash("Mtambo umesajiliwa kikamilifu!")
    return redirect(url_for('maintenance'))

# FEATURE 8: Electrical & Upload Backend
@app.route('/electrical', methods=['GET', 'POST'])
def electrical():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Hakuna faili lililochaguliwa')
            return redirect(request.url)
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Hapa unaweza kuhifadhi jina la faili kwenye database
            return render_template('electrical.html', filename=filename)
    
    return render_template('electrical.html')

# FEATURE 9: API Endpoint kwa ajili ya Live Diagnosis (Mobile App ready)
@app.route('/api/check_fault/<string:code>')
def check_fault(code):
    # Hapa ungeweka logic ya kutafuta kwenye Database ya kweli
    return {"code": code, "result": "Boost Pressure High", "action": "Check Wiring J1-P2"}

# FEATURE 10: Error Handling
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
￼Enter
