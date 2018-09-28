import os

from api.app import create_app
import tasks.analysis
import tasks.build
from tasks.testing import (
    TestUnitsTask,
    TestIntegrationTask,
    RunServerTask
)

configuration_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'configuration')

DOCKER_APP_REPO_BASENAME = 'api'
BASE_IMAGE_NAME = 'docker-registry.jonahgroup.com/python27'
PACKAGE_INCLUDES = ['*.py', '*.ini', "*.html", "*.css", "*.json",
                    "*.png", "*.gif", "*.ico", "*.js", "*.po", "*.mo", "*.sh"]

clean_task = tasks.build.CleanTask()
complexity_task = tasks.analysis.ComplexityTask()
flake8_task = tasks.analysis.Flake8Task()
package_task = tasks.build.PackageTask(includes=PACKAGE_INCLUDES)
runserver_task = RunServerTask(create_app, configuration_path)
test_units_task = TestUnitsTask(DOCKER_APP_REPO_BASENAME)
test_integration_task = TestIntegrationTask()
