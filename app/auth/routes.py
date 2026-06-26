from flask import render_template, url_for, flash, redirect, request
from app.auth import auth
from app import bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import random
import datetime
from firebase_admin import auth as firebase_auth
from firebase_admin._auth_utils import EmailAlreadyExistsError
@auth.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        from flask import current_app
        from app.models import FirebaseUser
        
        if current_app.db_firestore:
            users_ref = current_app.db_firestore.collection('website')
            docs = users_ref.where('email', '==', email).limit(1).get()
            if docs:
                user_doc = docs[0]
                user_data = user_doc.to_dict()
                
                try:
                    if bcrypt.check_password_hash(user_data.get('kata_sandi', ''), password):
                        if user_data.get('peran') != 'Admin':
                            flash('Akses ditolak. Hanya Admin yang diizinkan untuk login ke panel ini.', 'danger')
                            return redirect(url_for('auth.login'))
                            
                        if not user_data.get('is_verified', False):
                            flash('Silakan verifikasi email Anda terlebih dahulu.', 'warning')
                            return redirect(url_for('auth.verify_email', email=email))
                        
                        user_obj = FirebaseUser(user_data, user_doc.id)
                        login_user(user_obj, remember=request.form.get('remember'))
                        next_page = request.args.get('next')
                        return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
                except ValueError:
                    # Menangkap error "Invalid salt" jika hash di Firestore menggunakan format yang salah (misalnya Werkzeug hash lama)
                    pass
                    
            flash('Login Unsuccessful. Please check email and password', 'danger')
        else:
            flash('Sistem Firestore belum aktif.', 'danger')
    return render_template('login.html', title='Login')

@auth.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        role_name = "Admin"
        
        from flask import current_app
        if current_app.db_firestore:
            users_ref = current_app.db_firestore.collection('website')
            docs = users_ref.where('email', '==', email).limit(1).get()
            if docs:
                flash('Email sudah terdaftar di Firestore. Silakan login.', 'danger')
                return redirect(url_for('auth.register'))
                
            # Create user in Firebase Authentication
            try:
                firebase_user = firebase_auth.create_user(
                    email=email,
                    password=password,
                    display_name=username
                )
            except EmailAlreadyExistsError:
                flash('Email sudah terdaftar di Firebase Authentication. Silakan gunakan email lain atau login.', 'danger')
                return redirect(url_for('auth.register'))
            except Exception as e:
                print(f"[ERROR] Gagal membuat user di Firebase Auth: {e}")
                flash(f'Terjadi kesalahan saat menghubungi Authentication server.', 'danger')
                return redirect(url_for('auth.register'))

            pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            
            otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            user_data = {
                'username': username,
                'email': email,
                'kata_sandi': pw_hash,
                'peran': role_name,
                'is_verified': False,
                'otp_code': otp_code
            }
            
            # Gunakan email (atau sanitasi email) sebagai Document ID agar mudah dicari
            doc_id = email
            user_doc_ref = users_ref.document(doc_id)
            user_doc_ref.set(user_data)
            
            # Send Email
            try:
                msg = Message('Verifikasi Akun GARDA Anda', recipients=[email])
                current_year = datetime.datetime.now().year
                msg.html = render_template('email_otp.html', username=username, otp_code=otp_code, year=current_year)
                mail.send(msg)
                print(f"[SUCCESS] Email OTP terkirim ke {email}")
            except Exception as e:
                print(f"[ERROR] Gagal mengirim email: {e}")
                print(f"[BACKUP] OTP UNTUK EMAIL {email} ADALAH: {otp_code}")
                flash('Gagal mengirim email, pastikan konfigurasi SMTP benar. Cek console untuk kode OTP.', 'warning')
            
            flash('Akun berhasil dibuat! Silakan cek email Anda untuk kode verifikasi.', 'success')
            return redirect(url_for('auth.verify_email', email=email))
        else:
            flash('Sistem Firestore belum siap.', 'danger')
        
    return render_template('register.html', title='Register')

@auth.route("/verify-email", methods=['GET', 'POST'])
def verify_email():
    email = request.args.get('email')
    
    if request.method == 'POST':
        email_post = request.form.get('email')
        otp_input = request.form.get('otp')
        
        from flask import current_app
        if current_app.db_firestore:
            users_ref = current_app.db_firestore.collection('website')
            docs = users_ref.where('email', '==', email_post).limit(1).get()
            if docs:
                user_doc = docs[0]
                user_data = user_doc.to_dict()
                
                if user_data.get('otp_code') == otp_input:
                    user_doc.reference.update({
                        'is_verified': True,
                        'otp_code': None
                    })
                    flash('Email berhasil diverifikasi! Silakan login.', 'success')
                    return redirect(url_for('auth.login'))
                else:
                    flash('Kode OTP tidak valid.', 'danger')
                    return redirect(url_for('auth.verify_email', email=email_post))
                    
        flash('Terjadi kesalahan sistem.', 'danger')
        
    return render_template('verify_email.html', title='Verifikasi Email', email=email)

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
