from flask import Blueprint, request, session, jsonify
from .models import User
import hashlib
def current_user():
    if 'id' in session:
        uid=session['id']
        return User.query.get(uid)
    return None


def split_by_crlf(s):
    return [v for v in s.splitlines() if v]


def json_response(message):
    data = {'message': message}
    return jsonify(data)

