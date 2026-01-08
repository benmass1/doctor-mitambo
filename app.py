from flask import Flask, render_template, request, flash, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "masanja_key_2024"

# FEATURE 1: Database kubwa ya Fault Codes (CAT & Komatsu)
FAULT_CODES = {
    "EID 0126-3": {"brand": "CAT", "tatizo": "Transmission Oil Filter Plugged", "gharama": 5, "level": "Critical", "ufumbuzi": "Badilisha filter na kagua presha ya mafuta."},
    "70-2": {"brand": "Komatsu", "tatizo": "Fuel Injector Sensor Fault", "gharama": 10, "level": "Warning", "ufumbuzi": "Kagua wiring harness ya sensor."},
    "E360": {"brand": "CAT", "tatizo": "Low Coolant Level", "gharama": 2, "level": "Minor", "ufumbuzi": "Ongeza maji na kagua leaks."},
    "1500-0": {"brand": "Komatsu", "tatizo": "High Hydraulic Temperature", "gharama": 8, "level": "Critical", "ufumbuzi": "Kagua hydraulic cooler na fan belt."},
}

# FEATURE 2: User Wallet System Simulation
# Kwenye mfumo kamili, hizi data zingetoka kwenye Database (SQL)
user_data = {
    "wallet": 100,
    "history": [],
    "last_login": datetime.now().strftime("%Y-%m-%d %H:%M")
}

@app.route('/')
def index():
    # FEATURE 3: Dashboard Overview
    return render_template('index.html', user=user_data)

@app.route('/diagnosis', methods=['GET', 'POST'])
def diagnosis():
    matokeo = None
    if request.method == 'POST':
        code = request.form.get('fault_code').upper().strip()
        
        # FEATURE 4: Search & Validation Logic
        if code in FAULT_CODES:
            data = FAULT_CODES[code]
            gharama = data['gharama']
            
            # FEATURE 5: Payment Gateway Logic (MGM Token Gate)
            if user_data["wallet"] >= gharama:
                user_data["wallet"] -= gharama
                matokeo = data
                
                # FEATURE 6: Transaction History Recording
                entry = f"Diagnosed {code} (-{gharama} MGM) - {datetime.now().strftime('%H:%M')}"
                user_data["history"].insert(0, entry)
                
                flash(f"Malipo ya MGM {gharama} yamefanikiwa!", "success")
            else:
                flash("MGM Hazitoshi! Nunua token uendelee.", "danger")
        else:
            flash("Kodi haipo kwenye mfumo. Wasiliana na Admin.", "warning")
            
    return render_template('diagnosis.html', matokeo=matokeo, user=user_data)

# FEATURE 7: Token Top-up (Buy MGM)
@app.route('/buy-tokens')
def buy_tokens():
    return render_template('buy_tokens.html', user=user_data)

# FEATURE 8: Maintenance Schedule (Coming Soon)
@app.route('/maintenance')
def maintenance():
    return render_template('maintenance.html')

if __name__ == '__main__':
    app.run(debug=True)
