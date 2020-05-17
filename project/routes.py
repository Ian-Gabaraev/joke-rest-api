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
        Process POST requests to endpoint '/register' w/
        required parameters str: username and str: password
        :return: 400 Bad Request if username or password
        are not alphanumeric or shorter than 6 chars each,
        bigger than 20 chars each, else return 201 Created
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
            return make_response('This user already exists', 400)
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


@app.route('/create-joke', methods=['PUT'])
@jwt_required
def create_joke():
    try:
        assert 'content' in request.form
    except AssertionError:
        return make_response('No joke content present', 400)
    else:
        try:
            assert len(request.form['content']) <= 900
        except AssertionError:
            return make_response('Joke string is too long. '
                                 'Max allowed size is 900 characters', 400)
        else:
            new_joke = Joke(
                content=request.form['content'],
                user_id=get_jwt_identity()
            )
            db.session.add(new_joke)
            db.session.commit()
            return make_response('Joke created', 201)
    finally:
        log_action(request, get_jwt_identity())


@app.route('/get-joke-by-id')
@jwt_required
def get_joke_by_id():
    try:
        assert 'joke_id' in request.form
    except AssertionError:
        return make_response('joke_id is a required parameter', 400)
    else:
        try:
            joke_obj = Joke.query.filter_by(
                joke_id=request.form['joke_id'],
                user_id=get_jwt_identity()
            ).first()
            assert joke_obj
        except AssertionError:
            return make_response('Nothing found', 404)
        else:
            return make_response(
                joke_obj.content, 200
            )
    finally:
        log_action(request, get_jwt_identity())


@app.route('/my-jokes')
@jwt_required
def get_my_jokes():
    try:
        all_jokes = Joke.query.filter_by(user_id=get_jwt_identity()).all()
        assert all_jokes
    except AssertionError:
        return make_response('', 204)
    else:
        result = {
            k: v.content for (k, v) in enumerate(all_jokes)
        }
        return jsonify(result)


@app.route('/update-joke', methods=['PATCH'])
@jwt_required
def update_my_joke():
    pass


@app.route('/delete-joke', methods=['DELETE'])
@jwt_required
def delete_my_joke():
    pass


api = Api(app)
api.add_resource(Registration, '/register')
