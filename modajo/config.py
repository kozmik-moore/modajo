from os.path import join, exists

from instance import SECRET_KEY, STORAGE_PATH

MEMORY = 'sqlite://'


class Config(object):
    SECRET_KEY = SECRET_KEY or '9efdc4acf5de2e3b5dcf8a2322e41a024ae72504ad06e191'
    TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    Testing = True
    SQLALCHEMY_DATABASE_URI = MEMORY


class DevelopmentConfig(Config):
    db_uri = join(STORAGE_PATH, 'modajo.db')
    SQLALCHEMY_DATABASE_URI = db_uri if exists(db_uri) else MEMORY


class ProductionConfig(Config):
    db_uri = join(STORAGE_PATH, 'modajo.db')
    SQLALCHEMY_DATABASE_URI = db_uri


appconfig = {
    'testing': TestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
