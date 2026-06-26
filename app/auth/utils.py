from functools import wraps
from flask import abort
from flask_login import current_user

def roles_required(*role_names):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            
            user_role = getattr(current_user, 'role_name', None)
            if not user_role and hasattr(current_user, 'role') and current_user.role:
                user_role = current_user.role.name
                
            if user_role not in role_names:
                abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
