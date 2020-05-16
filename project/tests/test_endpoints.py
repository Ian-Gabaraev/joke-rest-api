import sys
import os
import unittest
import json
import random
from sqlalchemy.orm.exc import UnmappedInstanceError
# Fixes the relative import issue for Travis CI
sys.path.append(os.getcwd() + '/..')
from project import create_app
from project.models import User
from project.models import Joke
from project.models import Action
from project.models import db


app = create_app()

tester = app.test_client()


class TestIfTablesExist(unittest.TestCase):
    """
    Test if tables are present and initialized
    """
    def test_if_all_tables_are_present(self):
        with app.app_context():
            self.assertEqual(
                len(
                    set(db.engine.table_names()).difference(
                        set([table.__tablename__ for table
                             in db.Model.__subclasses__()])
                    )),
                0)


class IndexPageTestCase(unittest.TestCase):

    def test_empty_204_response_to_index_page(self):
        """
        Test if request to index page returns 204 No Content
        """
        response = tester.get('/', content_type='html/text')

        self.assertEqual(response.status_code, 204)


class RegistrationResourceTestCase(unittest.TestCase):
    """
    Test sign up functionality
    Test-case 1: register with good credentials
    Test-case 2: register under existing name
    Test-case 3: register with undersized credentials
    Test-case 4: register without password
    """

    @staticmethod
    def register_fake_user(username, password, feedback=False):
        """
        Create new user
        :param username: user's name
        :param password: user's password
        :param feedback: enable/disable feedback
        :return: if feedback == True -> Response
        """
        response = tester.post('/register', data=dict(
            username=username,
            password=password
        ))
        if feedback:
            return response

    @staticmethod
    def get_user_id(username):
        """
        Return user_id of said user
        :param username: user's name in User table
        :return: User.id object
        """
        with app.test_request_context():
            identity = User.query.filter_by(
                username=username).first().id
            return identity

    @staticmethod
    def get_user_object(username):
        """
        Get User object for said user
        :param username: user's name
        :return: User object
        """
        with app.app_context():
            user = User.query.filter_by(username=username).first()
        return user

    @staticmethod
    def delete_user(username):
        """
        Remove said user from User table
        :param username: user's name
        :return: None
        """
        with app.test_request_context():
            user = RegistrationResourceTestCase.get_user_object(username)
            try:
                db.session.delete(user)
                db.session.commit()
            except UnmappedInstanceError:
                pass

    def test_register_new_user(self):
        """
        Test if newly created user is in User table
        and status code is 201 Created
        """
        response = RegistrationResourceTestCase.register_fake_user(
            app.config['FAKE_USER'],
            app.config['FAKE_USER_PASSWORD'],
            feedback=True
        )
        self.fake_user = RegistrationResourceTestCase.get_user_object(
                username=app.config['FAKE_USER'])
        self.assertTrue(self.fake_user)
        self.assertEqual(response.status_code, 201)

    def test_attempt_to_register_under_existing_username(self):
        """
        Then, test if attempt to register under existing username
        returns 400 Bad Request
        """
        RegistrationResourceTestCase.register_fake_user(
            app.config['FAKE_USER'],
            app.config['FAKE_USER_PASSWORD'],
            feedback=False
        )
        response = RegistrationResourceTestCase.register_fake_user(
            app.config['FAKE_USER'],
            app.config['FAKE_USER_PASSWORD'],
            feedback=True
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'This user already exists')

    def test_registration_with_wrongly_sized_credentials(self):
        """
        Test if request to registration resource with
        wrongly sized credentials returns 400 Bad Request
        """
        response = tester.post('/register', data=dict(
            username='ian', password=100
        ))

        self.assertEqual(response.status_code, 400)

    def test_registration_with_missing_credential(self):
        """
        Test if request to registration resource without
        password returns 400 Bad Request
        """
        response = tester.post('/register', data=dict(
            username='ian'
        ))

        self.assertEqual(response.status_code, 400)

    def tearDown(self):
        """
        Remove the fake row from the User table
        """
        RegistrationResourceTestCase.delete_user(
            username=app.config['FAKE_USER']
        )


# REFACTORED
class LoginTestCase(unittest.TestCase):
    """
    Test log in functionality
    Test-case 1: log in with good credentials
    Test-case 2: log in with bad password
    Test-case 3: log in unregistered user
    Test-case 4: log in without password
    """

    @staticmethod
    def login_fake_user(username, password, jwt=False):
        """
        Log in said user
        :param username: user's name
        :param password: user's password
        :param jwt: enable to return JWT
        :return: if jwt == False -> Response, else JWT
        """
        response = tester.post('/login', data=dict(
            username=username,
            password=password
        ))
        if not jwt:
            return response
        return json.loads(response.data.decode('utf-8'))['access_token']

    def setUp(self):
        """
        First, register a new user in the User table
        """
        tester.post('/register', data=dict(
            username=app.config['FAKE_USER'],
            password=app.config['FAKE_USER_PASSWORD']
        ))

    def test_attempt_to_login_a_registered_user_with_correct_credentials(self):
        """
        Test if logging in with correct credentials returns 200 OK
        and contains a JWT
        """
        response = LoginTestCase.login_fake_user(
            username=app.config['FAKE_USER'],
            password=app.config['FAKE_USER_PASSWORD']
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', json.loads(response.data.decode('utf-8')))

    def test_attempt_to_login_a_registered_user_with_wrong_password(self):
        """
        Test if logging in with wrong password returns 401 Unauthorized
        """
        response = LoginTestCase.login_fake_user(
            username=app.config['FAKE_USER'],
            password='deliberately'
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, b'Wrong password')

    def test_attempt_to_login_an_unregistered_user(self):
        """
        Test if logging in with wrong username returns 401 Unauthorized
        """
        response = LoginTestCase.login_fake_user(
            username='dummyusername',
            password='dummpassword'
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, b'No such user')

    def test_attempt_to_login_without_a_credential(self):
        """
        Test if logging in with wrong password returns 400 Bad Request
        """
        response = tester.post('/login', data=dict(
            username=app.config['FAKE_USER'],
        ))
        self.assertEqual(response.status_code, 400)

    def tearDown(self):
        """
        Remove the fake row from the User table
        """
        RegistrationResourceTestCase.delete_user(
            username=app.config['FAKE_USER']
        )


class BasicJokesResourceTestCase(unittest.TestCase):
    """
    Test creating jokes with JWT
    Test-case 1: create joke with proper parameters
    Test-case 2: attempt to create over-sized joke
    Test-case 3: attempt to create joke without content
    """

    access_token = None

    humongous_string = ''.join(
        [chr(random.randint(65, 122)) for _ in range(901)]
    )

    @staticmethod
    def get_joke_id(user_id, content):
        """
        Retrieve joke_id of said joke
        :param user_id: joke owner's user_id
        :param content: joke text
        :return: int joke_id
        """
        with app.app_context():
            this_joke = Joke.query.filter_by(
                user_id=user_id,
                content=content).first()
            return this_joke

    @staticmethod
    def create_joke(content, access_token, feedback=False):
        """
        Create new joke in Joke table
        :param content: joke text
        :param access_token: JSON Web Token
        :param feedback: enable/disable feedback
        :return: if feedback == True -> Response
        """
        response = tester.put(
            '/create-joke',
            data=dict(
                content=content),
            headers=dict(Authorization='Bearer ' + access_token)
        )
        if feedback:
            return response

    @staticmethod
    def delete_joke(user_id, content):
        """
        Delete said joke from Joke table
        :param user_id: joke owner's user_id
        :param content: joke text
        :return: None
        """
        with app.test_request_context():
            fake_joke = Joke.query.filter_by(
                user_id=user_id,
                content=content
            ).first()
            db.session.delete(fake_joke)
            db.session.commit()

    def setUp(self):
        # First, register a new user in the User table"""
        RegistrationResourceTestCase.register_fake_user(
            app.config['JOKE_FAKE_USER'],
            app.config['JOKE_FAKE_USER_PASSWORD']
        )

        # Then, log in and retrieve JWT
        self.access_token = LoginTestCase.login_fake_user(
            app.config['JOKE_FAKE_USER'],
            app.config['JOKE_FAKE_USER_PASSWORD'],
            jwt=True
        )

        # Get id of User than made the request
        self.identity = RegistrationResourceTestCase.get_user_id(
            app.config['JOKE_FAKE_USER']
        )

    def test_creating_a_joke_with_correct_parameters(self):
        """
        Test if submitting correct parameters to
        create-joke endpoint returns 201 Created
        """
        # Create new joke
        response = BasicJokesResourceTestCase.create_joke(
            content=app.config['FAKE_JOKE'],
            access_token=self.access_token,
            feedback=True
        )

        # Get the newly created joke
        this_joke = BasicJokesResourceTestCase.get_joke_id(
            user_id=self.identity,
            content=app.config['FAKE_JOKE']
        )

        # Check if the newly created joke is present in the Joke table
        # and response code is 201 Created
        self.assertTrue(this_joke)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, b'Joke created')

        # Remove the fake joke from the Joke table
        BasicJokesResourceTestCase.delete_joke(
            user_id=self.identity,
            content=app.config['FAKE_JOKE']
        )

    def test_fail_on_submitting_humongous_string(self):
        """
        Test if submitting large text (> 900 chars)
        yields 400 Bad Request
        """
        response = BasicJokesResourceTestCase.create_joke(
            content=self.humongous_string,
            access_token=self.access_token,
            feedback=True
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, app.config['TOO_LONG'])

    def test_fail_on_omitting_content(self):
        """
        Test if omitting 'content' in request parameters
        yields 400 Bad Request
        """
        response = tester.put('/create-joke', headers=dict(
            Authorization='Bearer ' + self.access_token)
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'No joke content present')

    def tearDown(self):
        RegistrationResourceTestCase.delete_user(
            username=app.config['JOKE_FAKE_USER']
        )


class RetrieveJokeTestCase(unittest.TestCase):
    pass


class UpdateJokeTestCase(unittest.TestCase):
    pass


class DeleteJokeTestCase(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()