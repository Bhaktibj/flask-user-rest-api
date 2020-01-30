import json
import time
from flask import Blueprint, request, session
from flask import render_template
from werkzeug.security import gen_salt
from .models import db, User, OAuth2Client
from .oauth2 import authorization
from .utils import current_user, split_by_crlf, json_response


bp_obj=Blueprint(__name__, 'print', template_folder='template')


@bp_obj.route('/')
def home():
    return render_template('home.html')


@bp_obj.route('/create', methods=['POST'])
def create_user():
    if request.method == 'POST':
        username=request.json.get('username')
        if username is None:
            return json_response("username is required")
        email=request.json.get('email')
        if email is None or email is '':
            return json_response("email is required")
        password=request.json.get('password')
        confirm_password=request.json.get('confirm_password')
        if password and confirm_password is None:
            return json_response("password is required")
        elif password != confirm_password:
            return json_response("Please confirm your password")
        user=User.query.filter_by(username=username, password=password).first()
        if not user:
            user=User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()
        session['id']=user.id
    user=current_user()
    print("user:", user.id)
    data={}
    client_data=[]
    if user:
        clients=OAuth2Client.query.filter_by(user_id=user.id).all()
        for client in clients:
            print(client, "client")
            for key, value in vars(client).items():
                data.update({key: value})
        client_data.append(data)
    else:
        client_data=[]
    try:
        del data['_sa_instance_state']
    except:
        return json_response(client_data)
    return json_response(client_data)


@bp_obj.route('/login', methods=('GET','POST'))
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username=request.json.get('username')
        if username is None:
            return json_response("please enter username")
        password=request.json.get('password')
        if password is None:
            return json_response("please enter password")
        user=User.query.filter_by(username=username, password=password).first()
        if user:
            session['id']=user.id
            return json_response("Login is successfully" + ' ' + username)
        else:
            return json_response("Forgot password")


@bp_obj.route('/create_client', methods=['POST'])
def create_client():
    user=current_user()
    print(user.id)
    client_id=gen_salt(24)
    client_id_issued_at=int(time.time())
    client=OAuth2Client(
        client_id=client_id,
        client_id_issued_at=client_id_issued_at,
        user_id=user.id
    )
    print(client)
    if client.token_endpoint_auth_method == 'none':
        client.client_secret=''
    else:
        client.client_secret=gen_salt(48)
    data=json.loads(request.data)
    print(data)
    client_metadata={
        "client_name": data["client_name"],
        "client_uri": data["client_uri"],
        "redirect_uri": data["redirect_uri"],
        "grant_types": split_by_crlf(data["allowed_grant_types"]),
        "response_types": split_by_crlf(data["allowed_response_types"]),
        "scope": data["allowed_scope"],
        "token_endpoint_auth_method": data["token_endpoint_auth_method"]
    }
    client.set_client_metadata(client_metadata)
    db.session.add(client)
    db.session.commit()
    return json_response(client_metadata)


@bp_obj.route('/logout')
def logout():
    try:
        print(session['id'])
        del session['id']
    except:
        return json_response("out of session")
    return json_response("logout sucessfully")


@bp_obj.route('/forgot', methods=['POST'])
def forgot_password():
    if request.method == 'POST':
        username=request.json.get('username')
        if username is None or username is '':
            return json_response("username is required")
        new_password=request.json.get('new_password')
        if new_password is None or new_password is '':
            return json_response("new password is required")
        user=User.query.filter_by(username=username).first()
        print(user)
        if not user:
            return json_response("User is not found")
        user.password=new_password
        db.session.add(user)
        db.session.commit()
        return json_response("password is changed")


@bp_obj.route('/reset_pass', methods=['POST'])
def reset_password():
    if request.method == 'POST':
        username=request.json.get('username')
        old_password = request.json.get('old_password')
        if username and old_password is None:
            return json_response("username or password is required")
        new_password=request.json.get('new_password')
        if new_password is None or new_password is '':
            return json_response("new password is required")
        confirm_password=request.json.get('confirm_password')
        if new_password and confirm_password is None:
            return json_response("password is required")
        if new_password != confirm_password:
            return json_response("Please confirm your password")
        user = User.query.filter_by(username=username, password=old_password).first()
        print(user)
        if not user:
            return json_response("User is not found")
        if old_password == confirm_password:
            return json_response("Your password is same please enter another password")
        user.password = confirm_password
        db.session.add(user)
        db.session.commit()
        return json_response("new password is set")


@bp_obj.route('/oauth/token', methods=['POST'])
def issue_token():
    return authorization.create_token_response()
