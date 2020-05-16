"""Flask configuration"""


class Config:
    """Setting up config variables"""

    # General
    FLASK_ENV = "development"
    TESTING = True

    # Database
    SQLALCHEMY_DATABASE_URI = "sqlite:///sqlite_db/catalogue.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = 'super-secret'

    # Tests
    FAKE_DATABASE_URI = "sqlite:///tests/test.db"
    FAKE_USER = 'bajekcreed09'
    FAKE_USER_PASSWORD = 'xenomorpH9021'
    FAKE_JOKE = 'A horse and a pigeon walk into a bar...'

    # Messages
    BAD_PARAMETER = "User\'s name can only contain digits " \
                    "and letters and must be at least 6 " \
                    "characters long, 20 characters at max"
