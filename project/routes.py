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
        for param in Registration.parser.parse_args():
            if not param.isalnum() or not len(param) >= 6:
                return make_response(jsonify(
                    error='User\'s name can only '
                          'contain digits and letters and '
                          'must be at least 6 characters long'
                ), 400)

        return make_response('', 201)


api = Api(app)
api.add_resource(Registration, '/register')
