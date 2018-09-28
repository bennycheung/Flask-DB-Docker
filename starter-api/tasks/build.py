import os

from fabric.api import lcd
from fabric.operations import local
from fabric.tasks import Task
import formic

from . import constants


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


class CleanTask(Task):
    """Delete generated files and directories."""
    name = 'clean'

    def run(self):
        local('rm -fr {0}'.format(constants.PACKAGE_DIRECTORY))
        local('rm -fr {0}'.format(constants.TEST_RESULTS_DIRECTORY))
        local('rm -fr .coverage')
        local('find . -name "*.pyc" -delete')


class PackageTask(Task):
    """Bundle the app and virtual environment in to a zip file for deployment.

    The package file will be called package/content.zip and will include the
    active virtual environment copied to the directory .virtualenvs/virtualenv.
    """
    name = 'package'

    def __init__(self, includes=None, excludes=None):
        """Creates a package task. Use includes and excludes to provide a list of
        Ant-style globs to specify the files to be included and excluded in the
        package. See http://www.aviser.asia/formic/ for more about globs.
        """
        super(PackageTask, self).__init__()
        if includes is None:
            self.includes = [
                '*.py',
                'base.txt',
                '*.xml'
            ]
        else:
            self.includes = includes
        if excludes is None:
            self.excludes = [
                'package/**/*',
                'tests/**/*',
            ]
        else:
            self.excludes = excludes

    def _copy_files(self, staging_dir, includes, excludes):
        package_files = formic.FileSet(includes, excludes)
        for directory, file_name in package_files.files():
            if directory:
                target_path = os.path.join(staging_dir, directory, file_name)
                create_dir(os.path.join(staging_dir, directory))
            else:
                target_path = os.path.join(staging_dir, file_name)
            local('cp {0} {1}'.format(os.path.join(directory, file_name), target_path))

    def run(self):
        staging_dir = os.path.join(constants.PACKAGE_DIRECTORY, constants.APP_CONTENT_DIRECTORY)
        if os.path.exists(staging_dir):
            local('rm -rf ' + staging_dir)

        create_dir(staging_dir)
        os.chmod(staging_dir, 0755)

        virtual_env_dir = os.environ['VIRTUAL_ENV']
        directory = os.path.join(staging_dir, '.virtualenvs')
        if not os.path.exists(directory):
            os.mkdir(directory)
        directory = os.path.join(directory, constants.VIRTUALENV_NAME_IN_PACKAGE)
        if not os.path.exists(directory):
            local('cp -R -L {0} {1}'.format(virtual_env_dir, directory))

        self._copy_files(staging_dir, self.includes, self.excludes)

        with lcd(constants.PACKAGE_DIRECTORY):
            local('zip -r {0} {1}'.format(constants.APP_CONTENT_DIRECTORY + ".zip", constants.APP_CONTENT_DIRECTORY))
