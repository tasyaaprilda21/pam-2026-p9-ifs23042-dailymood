from flask import Blueprint, request, jsonify
from ..models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username, password=password).first()

    if not user:
        return jsonify({'message': 'Username atau password salah!'}), 401

    return jsonify({
        'message': 'Login berhasil!',
        'user': {
            'id': user.id,
            'username': user.username
        }
    }), 200