
import os

filepath = "app/main/routes.py"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_routes = """@main.route("/inbox")
@login_required
def inbox():
    from flask import current_app
    from firebase_admin import firestore
    
    requests_data = []
    
    if current_app.db_firestore:
        try:
            # 1. Fetch patients to map ID to Name
            patients_map = {}
            p_docs = current_app.db_firestore.collection("mobile").get()
            for doc in p_docs:
                p_data = doc.to_dict()
                p_id = str(p_data.get("id", doc.id))
                patients_map[p_id] = p_data.get("name", "Unknown Patient")
                
            # 2. Fetch requests from multiple possible collections
            collections_to_check = ["inbox", "requests_perawat", "requests_dokter"]
            
            for coll in collections_to_check:
                req_ref = current_app.db_firestore.collection("website").document(current_user.email).collection(coll)
                req_docs = req_ref.order_by("waktu", direction=firestore.Query.DESCENDING).get()
                
                for doc in req_docs:
                    data = doc.to_dict()
                    if data.get("status") == "selesai":
                        continue
                    data["id"] = doc.id
                    data["collection"] = coll
                    data["nama_pasien"] = patients_map.get(str(data.get("id_pasien")), "Tidak ada pasien terkait")
                    
                    if data.get("waktu"):
                        data["waktu_str"] = data["waktu"].strftime("%d %b %Y, %H:%M")
                    else:
                        data["waktu_str"] = "Baru saja"
                        
                    requests_data.append(data)
                    
        except Exception as e:
            print(f"Error fetching inbox: {e}")
            
    return render_template("inbox.html", title="Inbox Komunikasi", requests=requests_data)

@main.route("/send_custom_request", methods=["POST"])
@login_required
def send_custom_request():
    from flask import current_app, flash
    from firebase_admin import firestore
    
    email_tujuan = request.form.get("email_tujuan")
    keterangan = request.form.get("keterangan")
    
    if not email_tujuan or not keterangan:
        flash("Email tujuan dan keterangan wajib diisi.", "warning")
        return redirect(request.referrer or url_for("main.dashboard"))
        
    if current_app.db_firestore:
        try:
            current_app.db_firestore.collection("website").document(email_tujuan).collection("inbox").add({
                "email_pengirim": current_user.email,
                "nama_pengirim": current_user.username,
                "keterangan": keterangan,
                "waktu": firestore.SERVER_TIMESTAMP,
                "status": "pending",
                "tipe": "custom_request"
            })
            flash(f"Pesan berhasil dikirim ke {email_tujuan}.", "success")
        except Exception as e:
            print(f"Error sending custom request: {e}")
            flash("Gagal mengirim pesan.", "danger")
            
    return redirect(request.referrer or url_for("main.dashboard"))

@main.route("/reply_and_approve/<collection>/<req_id>", methods=["POST"])
@login_required
def reply_and_approve(collection, req_id):
    from flask import current_app, flash
    from firebase_admin import firestore
    
    balasan = request.form.get("balasan")
    if not balasan:
        flash("Anda wajib mengisi balasan sebelum menyetujui request.", "warning")
        return redirect(url_for("main.inbox"))
        
    if current_app.db_firestore:
        try:
            req_ref = current_app.db_firestore.collection("website").document(current_user.email).collection(collection).document(req_id)
            doc = req_ref.get()
            
            if doc.exists:
                # Update status and save reply
                req_ref.update({
                    "status": "selesai",
                    "balasan": balasan,
                    "waktu_balasan": firestore.SERVER_TIMESTAMP
                })
                
                # Optionally send a notification back to the sender if we wanted to
                
                flash("Request berhasil dibalas dan diselesaikan.", "success")
            else:
                flash("Request tidak ditemukan.", "danger")
        except Exception as e:
            print(f"Error replying to request: {e}")
            flash("Gagal memproses request.", "danger")
            
    return redirect(url_for("main.inbox"))

"""

with open(filepath, "w", encoding="utf-8") as f:
    f.writelines(lines[:301]) # 0 to 300 (which is line 301)
    f.write(new_routes)
    f.writelines(lines[492:]) # 493 to end

print("Successfully replaced lines 302-492 with unified inbox routes.")

