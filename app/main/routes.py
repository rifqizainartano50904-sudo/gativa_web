from flask import render_template, request, url_for, redirect, flash, jsonify
from app.main import main
from flask_login import login_required, current_user
from app.auth.utils import roles_required

@main.route("/")
@main.route("/dashboard")
@login_required
def dashboard():
    from flask import current_app
    
    total_pasien = 0
    total_tk = 0
    
    if current_app.db_firestore:
        try:
            # Count pasien subcollection
            pasien_docs = current_app.db_firestore.collection('mobile').document('roles').collection('pasien').get()
            total_pasien = len(pasien_docs)
            
            # Count tenaga_kesehatan subcollection
            tk_docs = current_app.db_firestore.collection('mobile').document('roles').collection('tenaga_kesehatan').get()
            total_tk = len(tk_docs)
            
        except Exception as e:
            print(f"Error reading counts from Firestore: {e}")
            
    return render_template('dashboard.html', title='Dashboard', total_pasien=total_pasien, total_tk=total_tk)


@main.route("/data_pasien")
@login_required
@roles_required('Admin')
def data_pasien():
    from flask import current_app
    pasien_list = []
    if current_app.db_firestore:
        try:
            docs = current_app.db_firestore.collection('mobile').document('roles').collection('pasien').get()
            for doc in docs:
                p = doc.to_dict()
                p['id'] = doc.id
                pasien_list.append(p)
        except Exception as e:
            print(f"Error reading pasien from Firestore: {e}")
            
    return render_template('data_pasien.html', title='Data Pasien', users=pasien_list, collection='pasien')


@main.route("/data_tenaga_kesehatan")
@login_required
@roles_required('Admin')
def data_tenaga_kesehatan():
    from flask import current_app
    tk_list = []
    if current_app.db_firestore:
        try:
            docs = current_app.db_firestore.collection('mobile').document('roles').collection('tenaga_kesehatan').get()
            for doc in docs:
                p = doc.to_dict()
                p['id'] = doc.id
                tk_list.append(p)
        except Exception as e:
            print(f"Error reading tenaga kesehatan from Firestore: {e}")
            
    return render_template('data_tenaga_kesehatan.html', title='Data Tenaga Kesehatan', users=tk_list, collection='tenaga_kesehatan')

@main.route("/edit_user_data/<collection>/<doc_id>", methods=['POST'])
@login_required
@roles_required('Admin')
def edit_user_data(collection, doc_id):
    from flask import current_app, redirect, url_for, flash, request
    if collection not in ['pasien', 'tenaga_kesehatan']:
        flash("Koleksi tidak valid.", "danger")
        return redirect(url_for('main.dashboard'))
        
    if current_app.db_firestore:
        try:
            new_name = request.form.get('name')
            new_email = request.form.get('email')
            new_password = request.form.get('password')
            
            update_data = {}
            if new_name: update_data['name'] = new_name
            if new_email: update_data['email'] = new_email
            if new_password:
                from app import bcrypt
                update_data['password'] = bcrypt.generate_password_hash(new_password).decode('utf-8')
                
            if update_data:
                # Use subcollection
                current_app.db_firestore.collection('mobile').document('roles').collection(collection).document(doc_id).update(update_data)
                flash('Data berhasil diperbarui!', 'success')
        except Exception as e:
            flash(f'Gagal memperbarui data: {e}', 'danger')
            
    if collection == 'pasien':
        return redirect(url_for('main.data_pasien'))
    else:
        return redirect(url_for('main.data_tenaga_kesehatan'))
