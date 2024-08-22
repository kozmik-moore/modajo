from logging.config import dictConfig

from flask import Flask

from modajo.config import appconfig
from modajo.extensions import db, migrate

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


def create_app(configuration: str = None):
    _app = Flask('modajo', instance_relative_config=True)
    _app.logger.info('Initializing modajo...')

    # Set configuration
    _app.logger.info(f'Setting configuration to "{configuration}"...')
    cfgdict = appconfig['development']
    if configuration and configuration in appconfig:
        cfgdict = appconfig[configuration]
    elif configuration:
        _app.logger.warning(f'"{configuration}" not found in configuration options. '
                            f'Configuration set to "development".')
    else:
        _app.logger.warning('Configuration set to "development."')
    _app.config.from_object(cfgdict)

    # Initialize extensions
    _app.logger.info('Initializing extensions...')
    db.init_app(_app)
    migrate.init_app(_app)

    _app.logger.info('Creating new tables, as necessary...')
    with _app.app_context():
        from modajo import models
        db.create_all()

        # Register blueprints here

        # Init command line interfaces

        _app.logger.info('modajo has been successfully initialized!')

if __name__ == "__main__":
    pass
