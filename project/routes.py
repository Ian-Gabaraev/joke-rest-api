from flask import current_app as app
from flask import jsonify
from flask import request
from flask import make_response

from flask_restful import Resource
from flask_restful import Api
from flask_restful import reqparse

from sqlalchemy.exc import IntegrityError

from .models import User
from .models import Joke
from .models import Action
from .models import db

from . import bcrypt

from datetime import datetime

from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity

jwt = JWTManager(app)


@app.route('/')
def index():
    return '', 204


def log_action(req_obj: request, user_id: int):
    new_action = Action(
        user_ip_address=req_obj.remote_addr,
        action_time=datetime.now(),
        action_path=req_obj.path,
        user_id=user_id,
    )
    db.session.add(new_action)
    db.session.commit()


def compare(candidate: str, hashcode: str) -> bool:
    return bcrypt.check_password_hash(hashcode, candidate)


class Registration(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        'username',
        type=str,
        required=True
    )
    parser.add_argument(
        'password',
        type=str,
        required=True
    )

    def post(self):
        """
        Processes POST requests to endpoint /register w/
        required parameters str: username and str: password
        :return: 400 Bad Request if username or password
        are not alphanumeric or shorter than 6 chars each
        Else, return 201 Created
        """
        for param in Registration.parser.parse_args().values():
            if not param.isalnum() or (len(param) < 6 or len(param) > 20):
                return make_response(jsonify(
                    error=app.config['BAD_PARAMETER']
                ), 400)

        new_user = User(
            username=Registration.parser.parse_args()['username'],
            password=bcrypt.generate_password_hash(
                Registration.parser.parse_args()['password'])
        )
        try:
            db.session.add(new_user)
            db.session.commit()
        # Trying to add a UNIQUE field twice violates database integrity
        except IntegrityError:
            return make_response('This username already exists', 400)
        else:
            return make_response('User created', 201)


@app.route('/login', methods=['POST'])
def login():
    if not (request.form['username'] and request.form['password']):
        return make_response('Missing username/password', 401)

    if not User.query.filter_by(username=request.form['username']).first():
        return make_response('No such user', 401)

    if not compare(candidate=request.form['password'],
                   hashcode=User.query.filter_by(
                       username=request.form['username']).first().password):
        return make_response('Wrong password', 401)

    access_token = create_access_token(
        identity=User.query.filter_by(
            username=request.form['username']).first().id
    )

    return jsonify(access_token=access_token), 200


api = Api(app)
api.add_resource(Registration, '/register')
