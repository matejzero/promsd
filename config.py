# -------------------

# Daemon settings
# Listening port
PORT = 4999
# Path for YAML files ingested by Prometheus file SD. If path doesn't exists, it will be recursively created.
PROMETHEUS_YAML_DIR = "yaml"

# Database
DATABASE = "targets.db"

# Logging
LOG_FILE = "promsd.log"
LOG_LEVEL = "DEBUG"

DEBUG = True

# logging.basicConfig(
#     filename=LOG_FILE,
#     level=logging.INFO,
#     format='%(levelname)s: %(asctime)s pid:%(process)s module:%(module)s %(message)s',
#     datefmt='%d/%m/%y %H:%M:%S',
# )

# --------------------------------------

# TODO: Not working, since models.py can't load config.DATABASE


class Config(object):
    DATABASE = "targets.db"
    PORT = 4999

    LOGGER_NAME = "promsd"
    LOG_FILE = "promsd.log"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    PROM_YAML_PATH = "yaml"


class ProdConfig(Config):
    """Production configuration."""

    LOG_LEVEL = "INFO"
    DEBUG = False


class DevConfig(Config):
    """Development configuration."""

    DATABASE = ":memory:"
    LOG_LEVEL = "DEBUG"
    DEBUG = True


config = {
    'development': DevConfig,
    'production': ProdConfig,

    'default': DevConfig
}
