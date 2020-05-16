from flask import current_app as app
from flask import jsonify
from flask import make_response
from flask_restful import Resource
from flask_restful import Api
from flask_restful import reqparse
from sqlalchemy.exc import IntegrityError
from .models import User
from .models import Joke
from .models import Action
from .models import db
from passlib.hash import sha256_crypt


@app.route('/')
def index():
    return '', 204


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
            password=sha256_crypt.hash(Registration.parser.parse_args()['password'])
        )
        try:
            db.session.add(new_user)
            db.session.commit()
        # Trying to add a UNIQUE field twice violates database integrity
        except IntegrityError:
            return make_response('This username is occupied', 400)
        else:
            return make_response('User created', 201)


api = Api(app)
api.add_resource(Registration, '/register')
