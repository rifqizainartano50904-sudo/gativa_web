from flask import request, jsonify, current_app
from app.api import api
from datetime import datetime
from firebase_admin import firestore
import traceback

def get_firestore():
    return current_app.db_firestore

# Helper to check required fields
def check_fields(data, required):
    missing = [f for f in required if f not in data]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    return True, ""

# --------------------------
# PATIENT AUTHENTICATION
# --------------------------
@api.route('/mobile/login', methods=['POST'])
def mobile_login():
    """
    Login endpoint for Patient.
    Since we don't have a global patient login right now, we search all doctors' patients.
    Payload: {"patient_email": "x@x.com", "password": "123"} 
    """
    data = request.get_json()
    ok, msg = check_fields(data, ['patient_email', 'password'])
    if not ok: return jsonify({"error": msg}), 400
    
    db = get_firestore()
    if not db: return jsonify({"error": "Database not ready"}), 500
    
    email = data['patient_email']
    password = data['password']
    
    # We will do a Collection Group Query across all 'patients' subcollections
    try:
        patients_query = db.collection('mobile').where('email', '==', email).limit(1).get()
        if not patients_query:
            return jsonify({"error": "Patient not found"}), 404
            
        patient_doc = patients_query[0]
        patient_data = patient_doc.to_dict()
        
        # Verify password (in a real app, hash checking)
        if str(patient_data.get('password', '')) != str(password):
            return jsonify({"error": "Invalid credentials"}), 401
            
        # Get the doctor's email (parent document)
        doctor_email = patient_data.get('email_dokter', patient_data.get('doctor_email', 'unknown_doctor@garda.com'))
        
        return jsonify({
            "message": "Login successful",
            "patient_id": patient_doc.id,
            "doctor_email": doctor_email,
            "patient_data": patient_data
        }), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# --------------------------
# PATIENT DASHBOARD & PROFILE
# --------------------------
@api.route('/mobile/dashboard', methods=['GET'])
def mobile_dashboard():
    """
    Get patient dashboard info.
    Query Params: doctor_email, patient_id
    """
    doctor_email = request.args.get('doctor_email')
    patient_id = request.args.get('patient_id')
    
    if not doctor_email or not patient_id:
        return jsonify({"error": "Missing doctor_email or patient_id"}), 400
        
    db = get_firestore()
    try:
        doc = db.collection('mobile').document(patient_id).get()
        if not doc.exists:
            return jsonify({"error": "Patient not found"}), 404
            
        return jsonify({"data": doc.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --------------------------
# OCR FOOD SCAN LOGGING
# --------------------------
@api.route('/mobile/scan', methods=['POST'])
def mobile_scan():
    """
    Receiving OCR food scan data from mobile app.
    Payload: {"doctor_email": "...", "patient_id": "...", "food_name": "Sarden X", "sodium_mg": 800}
    """
    data = request.get_json()
    ok, msg = check_fields(data, ['doctor_email', 'patient_id', 'food_name', 'sodium_mg'])
    if not ok: return jsonify({"error": msg}), 400
    
    db = get_firestore()
    try:
        doctor_email = data['doctor_email']
        patient_id = data['patient_id']
        sodium_mg = float(data['sodium_mg'])
        
        patient_ref = db.collection('mobile').document(patient_id)
        doc = patient_ref.get()
        if not doc.exists:
            return jsonify({"error": "Patient not found"}), 404
            
        # Log the food
        db.collection('website').document(doctor_email).collection('catatan_makanan').add({
            'id_pasien': patient_id,
            'nama_makanan': data['food_name'],
            'natrium_mg': sodium_mg,
            'waktu_scan': firestore.SERVER_TIMESTAMP
        })
        
        # Update current sodium
        p_data = doc.to_dict()
        current_sodium = float(p_data.get('natrium_saat_ini', 0)) + sodium_mg
        limit = float(p_data.get('batas_natrium_harian', 2000))
        
        status = 'Aman'
        if current_sodium > limit:
            status = 'Bahaya'
        elif current_sodium > limit * 0.8:
            status = 'Peringatan'
            
        patient_ref.update({
            'natrium_saat_ini': current_sodium,
            'status': status
        })
        
        return jsonify({"message": "Scan recorded", "new_status": status, "current_sodium": current_sodium}), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# --------------------------
# FOOD CATALOGS
# --------------------------
@api.route('/mobile/catalogs', methods=['GET'])
def mobile_catalogs():
    """
    Get food catalogs for education/alternatives.
    Query Params: doctor_email
    """
    doctor_email = request.args.get('doctor_email')
    if not doctor_email:
        return jsonify({"error": "Missing doctor_email"}), 400
        
    db = get_firestore()
    try:
        docs = db.collection('website').document(doctor_email).collection('katalog_makanan').get()
        catalogs = []
        for d in docs:
            cat = d.to_dict()
            cat['id'] = d.id
            catalogs.append(cat)
        return jsonify({"data": catalogs}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --------------------------
# CHAT SYSTEM
# --------------------------
@api.route('/mobile/chat', methods=['GET', 'POST'])
def mobile_chat():
    """
    GET: Get chat messages. Query Params: doctor_email, patient_id
    POST: Send a new message. Payload: {"doctor_email": "...", "patient_id": "...", "message": "hello"}
    """
    db = get_firestore()
    
    if request.method == 'GET':
        doctor_email = request.args.get('doctor_email')
        patient_id = request.args.get('patient_id')
        if not doctor_email or not patient_id:
            return jsonify({"error": "Missing params"}), 400
            
        try:
            docs = db.collection('website').document(doctor_email).collection('pesan')\
                     .where('id_pasien', '==', str(patient_id))\
                     .order_by('waktu').limit(50).get()
            
            msgs = []
            for d in docs:
                m = d.to_dict()
                if 'timestamp' in m and m['timestamp']:
                    # Simple conversion to string for JSON serialization
                    m['timestamp'] = str(m['timestamp'])
                msgs.append(m)
            return jsonify({"data": msgs}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == 'POST':
        data = request.get_json()
        ok, msg = check_fields(data, ['doctor_email', 'patient_id', 'message'])
        if not ok: return jsonify({"error": msg}), 400
        
        try:
            db.collection('website').document(data['doctor_email']).collection('pesan').add({
                'id_pasien': str(data['patient_id']),
                'id_pengirim': str(data['patient_id']),
                'nama_pengirim': 'Pasien',
                'pesan': data['message'],
                'waktu': firestore.SERVER_TIMESTAMP
            })
            return jsonify({"message": "Chat sent successfully"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500
