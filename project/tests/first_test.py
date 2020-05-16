import sys
import os
import unittest
# Fixes the relative import issue for Travis CI
sys.path.append(os.getcwd() + '/..')
from project import create_app
from project.models import User
from project.models import Joke
from project.models import Action
from project.models import db

app = create_app()


class IndexPageTestCase(unittest.TestCase):

    tester = app.test_client()

    def test_empty_204_response_to_index_page(self):
        """Test if request to index page returns 204 No Content"""
        response = self.tester.get('/', content_type='html/text')

        self.assertEqual(response.status_code, 204)


class RegistrationResourceTestCase(unittest.TestCase):

    tester = app.test_client()

    def test_registration_with_correct_credentials(self):
        """Test if request to registration resource with
        correct credentials returns 201 Created"""
        response = self.tester.post('/register', data=dict(
            username='iangabaraev95', password='xenomorph121'))

        # Tearing down the changes to the User table
        # w/ flask test request context syntax
        with app.test_request_context():
            fake_user = User.query.filter_by(username='iangabaraev95').first()
            db.session.delete(fake_user)
            db.session.commit()

        self.assertEqual(response.status_code, 201)

    def test_registration_with_wrongly_sized_credentials(self):
        """Test if request to registration resource with
        wrongly sized credentials returns 400 Bad Request"""
        response = self.tester.post('/register', data=dict(
            username='ian', password=100
        ))

        self.assertEqual(response.status_code, 400)

    def test_registration_with_missing_credential(self):
        """Test if request to registration resource without
        password returns 400 Bad Request"""
        response = self.tester.post('/register', data=dict(
            username='ian'
        ))

        self.assertEqual(response.status_code, 400)


class RegisteringWithCustomUsernameTestCase(unittest.TestCase):

    tester = app.test_client()

    def setUp(self):
        """First, add a row with fake name to the User table"""
        self.tester.post('/register', data=dict(
            username=app.config['FAKE_USER'],
            password=app.config['FAKE_USER_PASSWORD']
        ))

    def test_attempt_to_register_under_existing_username(self):
        """Then, test if attempt to register under existing username
        returns 400 Bad Request"""
        response = self.tester.post('/register', data=dict(
                username=app.config['FAKE_USER'],
                password=app.config['FAKE_USER_PASSWORD']
        ))

        self.assertEqual(response.status_code, 400)

    def tearDown(self):
        """Remove the fake row from the User table"""
        with app.test_request_context():
            fake_user = User.query.filter_by(username=app.config['FAKE_USER']).first()
            db.session.delete(fake_user)
            db.session.commit()


class LoginTestCase(unittest.TestCase):

    tester = app.test_client()

    def setUp(self):
        """First, register a new user in the User table"""
        self.tester.post('/register', data=dict(
            username=app.config['FAKE_USER'],
            password=app.config['FAKE_USER_PASSWORD']
        ))

    def test_attempt_to_login_a_registered_user_with_correct_credentials(self):
        """Test if logging in with correct credentials returns 200 OK
        and a JWT
        """
        response = self.tester.post('/login', data=dict(
            username=app.config['FAKE_USER'],
            password=app.config['FAKE_USER_PASSWORD']
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn('JWT', response.args)

    def test_attempt_to_login_a_registered_user_with_wrong_password(self):
        """Test if logging in with wrong password returns 401 Unauthorized"""
        response = self.tester.post('/login', data=dict(
            username=app.config['FAKE_USER'],
            password='deliberatelywrong21'
        ))
        self.assertEqual(response.status_code, 401)

    def tearDown(self):
        """Remove the fake row from the User table"""
        with app.test_request_context():
            fake_user = User.query.filter_by(username=app.config['FAKE_USER']).first()
            db.session.delete(fake_user)
            db.session.commit()


class JokesResourceTestCase(unittest.TestCase):
    def test_creating_a_joke_with_correct_parameters(self):
        """Test if submitting correct parameters to
        create-joke endpoint returns 201 Created"""


if __name__ == '__main__':
    unittest.main()
