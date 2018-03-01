"""This is a simple Prometheus service discovery daemon, where services can register themselfs to Prometheus
for monitoring. """

from flask import Flask, jsonify, make_response
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from .models import db
from .models import Job, Target, Label
from .log import logger
from .utils import generate_targets_yaml


# from promsd.log import logger

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/spec'  # Our API url (can of course be a local resource)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Test application"
    },
    oauth_config={  # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
       'clientId': "your-client-id",
       'clientSecret': "your-client-secret-if-required",
       'realm': "your-realms",
       'appName': "your-app-name",
       'scopeSeparator': " ",
       'additionalQueryStringParams': {'test': "hello"}
    }
)
# TODO: Add logging for error (in case of exceptions & stuff) and request (when debuging, content of request, url, function,...)


# @app.route('/')
# def index():
#     return "Prometheus service discovery daemon in the making"
#
#
# @app.route("/spec")
# def spec():
#     return jsonify(swagger(app))


def create_app():
    app = Flask(__name__)
    app.config.update(dict(
        TESTING = True
    ))
    # app.config.from_object(config_object)
    # app.config.from_object()
    # app.config.from_object(config[config_name])

    # app.config.update(dict(
    #     PORT = 4449
    # #os.path.join(app.root_path, 'flaskr.db'),
    # #     DEBUG=True,
    # #     SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/',
    # #     USERNAME='admin',
    # #     PASSWORD='default'
    # ))
    # app.config.update(config or {})
    # app.config.from_envvar('FLASKR_SETTINGS', silent=True)

    # Connect to database (and create file if it doesn't exists
    db.connect(reuse_if_open=True)

    #    logging.info("DB engine is {}".format(current_app.config.DATABASE))

    if not Target.table_exists() or not Job.table_exists() or not Label.table_exists():
        init_db(db)

    # Register routes and error pages
    register_blueprints(app)
    register_error_pages(app)

    sample_data(db)

    # Generate YAML files from latest data in DB
    generate_targets_yaml()

    @app.route("/spec")
    def spec():
        return jsonify(swagger(app))
    # Start the app
    # app.run(debug=True, port=int(config.PORT))
    # app.run(debug=False, port=4999)

    return app


def register_blueprints(app):
    """ Register all blueprint modules """

    from .views import target_blueprint
    app.register_blueprint(target_blueprint)

    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


def register_error_pages(app):
    # Register global error handlers
    @app.errorhandler(400)
    def bad_request(error):
        response = jsonify({'message': error.description})
        response.status_code = 400
        return response


    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error': error.description}), 404)


    @app.errorhandler(409)
    def conflict(error):
        response = jsonify({'message': error.description})
        response.status_code = 409
        return response


    @app.errorhandler(422)
    def conflict(error):
        response = jsonify({'message': error.description})
        response.status_code = 422
        return response


def init_db(db):
    db.create_tables([Target, Job, Label])


def sample_data(db):
    # Create tables
    db.drop_tables([Target, Job, Label])
    db.create_tables([Target, Job, Label])

    # Create sample jobs, targets and labels
    sample_jobs = [{"name": "node", "port": "9110"},
                   {"name": "mysql", "port": "9113"},
                   {"name": "node2", "port": "9114"},
                   {"name": "slurm", "port": "9115"}]
    for sample in sample_jobs:
        Job.create(name=sample['name'], port=sample['port'])
        # print("Created job %s" % sample['name'])

    sample_targets = [{"host": "target2.examples.org", "job": "node"},
                      {"host": "target2.examples.org", "job": "mysql"}]
    for sample in sample_targets:
        Target.create(host=sample['host'], job=Job.select().where(Job.name == sample['job']).get())
        # print("Created target %s" % sample['host'])

    sample_labels = [{"label": "env", "value": "prod", "host": "target2.examples.org"},
                     {"label": "severity", "value": "critical", "host": "target2.examples.org"}]
    for sample in sample_labels:
        Label.create(label=sample['label'], value=sample['value'],
                     target=Target.select().where(Target.host == sample['host']).get())
        # print("Created label %s for target %s" % (sample['label'], sample['host']))

    logger.debug("Created sample data.")
