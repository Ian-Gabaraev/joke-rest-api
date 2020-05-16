import sys
import os
import unittest
# Fixes the relative import issue for Travis CI
sys.path.append(os.getcwd() + '/..')
from project import create_app

app = create_app()


class BasicTestCase(unittest.TestCase):

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

    def test_attempt_to_register_with_existing_username(self):
        """Test if attempt to register under existing username
        returns 400 Bad Request"""
        pass


class JokesResourceTestCase(unittest.TestCase):
    def test_creating_a_joke_with_correct_parameters(self):
        """Test if submitting correct parameters to
        create-joke endpoint returns 201 Created"""


if __name__ == '__main__':
    unittest.main()
