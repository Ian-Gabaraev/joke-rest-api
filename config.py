"""Flask configuration"""


class Config:
    """Setting up config variables"""

    # General
    FLASK_ENV = "development"
    TESTING = True

    # Database
    SQLALCHEMY_DATABASE_URI = "sqlite:///sqlite_db/catalogue.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Tests
    FAKE_DATABASE_URI = "sqlite:///tests/test.db"
    FAKE_USER: str = 'iangabaraev95'
    FAKE_USER_PASSWORD: str = 'xenomorpH9021'
    FAKE_JOKE: str = 'A horse and a pigeon walk into a bar...'
