from flask import current_app as app
from flask import Markup
from flask import Request
from flask import Response
from flask import jsonify
from flask import make_response
from flask_restful import Resource
from flask_restful import Api
from flask_restful import reqparse
from .models import User
from .models import Joke
from .models import Action


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
            if not param.isalnum() or not len(param) >= 6:
                return make_response(jsonify(
                    error=app.config['BAD_PARAMETER']
                ), 400)

        return make_response('User created', 201)


api = Api(app)
api.add_resource(Registration, '/register')
