import sys
import os
import unittest
sys.path.append(os.getcwd() + '/..')
from project import create_app

app = create_app()


class BasicTestCase(unittest.TestCase):
    def test_empty_204_response_to_index_page(self):
        """Test if request to index page returns 204 No Content"""
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 204)


class RegistrationResourceTestCase(unittest.TestCase):
    def test_registration_with_correct_credentials(self):
        """Test if request to registration resource with
        correct credentials returns 201 Created"""
        tester = app.test_client(self)
        username = 'iangabaraev'
        password = 'xenomorph'
        response = tester.post('/register', data=dict(
            username=username, password=password))
        self.assertEqual(response.status_code, 201)

    def test_registration_with_wrong_size_of_credentials(self):
        """Test if request to registration resource with
        wrongly sized credentials returns 400 Bad Request"""
        tester = app.test_client(self)
        username = 'a'
        password = 100
        response = tester.post('/register', data=dict(
            username=username, password=password
        ))
        self.assertEqual(response.status_code, 400)

    def test_registration_with_missing_credential(self):
        """Test if request to registration resource without
        password returns 400 Bad Request"""
        tester = app.test_client(self)
        username = 'ian'
        response = tester.post('/register', data=dict(
            username=username
        ))
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
