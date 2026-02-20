from functools import wraps
from models import UserModel
from flask_jwt_extended import get_jwt_identity, jwt_required

def admin_required(func):
    @wraps(func)
    @jwt_required(fresh=True)
    def check_admin(*args, **kwargs):
        current_user = get_jwt_identity()
        user = UserModel.query.get_or_404(current_user)

        if not user.admin_access:
            return {"message":"Admin access required"}, 403

        return func(*args, **kwargs)
    return check_admin