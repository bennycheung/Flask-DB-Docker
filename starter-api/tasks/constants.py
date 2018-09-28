"""Constants that define the project structure conventions upon which Fabrika is based."""

REQUIREMENTS_FILES = [
    'requirements.txt'
]

INTEGRATION_TEST_PATH = 'tests/integration'
UNIT_TEST_PATH = 'tests/unit'

RUNSERVER_TASK = 'runserver'
LOCAL_RUN_PORT = 5001

PACKAGE_DIRECTORY = 'package'
PACKAGE_FILENAME = 'application'
VIRTUALENV_NAME_IN_PACKAGE = 'virtualenv'

TEST_RESULTS_DIRECTORY = 'test_results'

APP_CONTENT_DIRECTORY = 'content'

BASE_REGISTRY = 'docker-registry.jonahgroup.com:80'

# default port exposed by containers
DEFAULT_APP_SERVICE_PORT = 8080

DOCKERFILE = """
FROM {base_image_repo}
ADD content.zip /content.zip
RUN unzip content.zip
RUN chown -R webuser:webgroup /local/opt/points/content
RUN rm /content.zip
"""
