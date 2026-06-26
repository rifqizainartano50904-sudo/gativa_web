from flask_login import UserMixin
from app import login_manager

class FirebaseUser(UserMixin):
    def __init__(self, user_data, doc_id):
        self.id = doc_id
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.password = user_data.get('kata_sandi')
        self.role_name = user_data.get('peran', user_data.get('nama_peran', 'Perawat'))
        self.is_verified = user_data.get('is_verified', False)

    def has_role(self, role_name):
        return self.role_name == role_name

@login_manager.user_loader
def load_user(user_id):
    from flask import current_app
    if current_app.db_firestore:
        doc = current_app.db_firestore.collection('website').document(user_id).get()
        if doc.exists:
            return FirebaseUser(doc.to_dict(), doc.id)
    return None
