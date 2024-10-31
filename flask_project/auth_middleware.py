from flask import request, make_response, jsonify
import jwt
from functools import wraps
from flask import current_app as app
from flask_project.models import Customer, Service_Professional

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        # ensure the jwt-token is passed with the headers
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token: # throw error if no token provided
            return make_response(jsonify({"message": "A valid token is missing!"}), 401)
        try:
            # decode the token to obtain user public_id
            data = jwt.decode(token, app.config['SECRET_KEY'] , algorithms=['HS256'])
            if data['role'] == 'customer':
                current_user = Customer.query.filter_by(email=data['email']).first()
            else:
                current_user = Service_Professional.query.filter_by(email=data['email']).first()
        except Exception as e:
            return make_response(jsonify({"message": str(e)}), 401)
         # Return the user information attached to the token
        return f(current_user, *args, **kwargs)
    return decorator