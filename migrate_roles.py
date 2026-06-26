import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate('serviceAccountKey.json')
try:
    firebase_admin.initialize_app(cred)
except ValueError:
    pass

db = firestore.client()

def migrate_roles():
    users_ref = db.collection('website')
    users = users_ref.stream()
    
    count = 0
    for user in users:
        data = user.to_dict()
        update_data = {}
        
        # Check if we need to migrate
        if 'nama_peran' in data or 'id_peran' in data or 'tipe' in data:
            if 'nama_peran' in data:
                update_data['peran'] = data['nama_peran']
                update_data['nama_peran'] = firestore.DELETE_FIELD
            if 'id_peran' in data:
                update_data['id_peran'] = firestore.DELETE_FIELD
            if 'tipe' in data:
                update_data['tipe'] = firestore.DELETE_FIELD
                
            if update_data:
                users_ref.document(user.id).update(update_data)
                count += 1
                print(f"Migrated user {user.id}")
                
    print(f"Migration complete. Updated {count} users.")

if __name__ == '__main__':
    migrate_roles()
