import distutils
import io
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time

from fabric.operations import local
from fabric.tasks import Task
import pip.req

from . import constants


def _run_server(temp_dir, command, port, **kwargs):
    """
    Run a test server in a separate process using Fabric, logging output to a log file in the given temp dir.
    """
    log_file = os.path.join(temp_dir, '{0}-output.log'.format(command))
    output = io.open(log_file, 'wt', buffering=1)

    s = socket.socket()
    assert s.connect_ex(('127.0.0.1', port)) != 0, "Something is already using port {0}.".format(port)

    server_options = []
    for key, value in kwargs.iteritems():
        server_options.append('{}={}'.format(key, value))
    shell_args = []
    shell_args.extend([
        distutils.spawn.find_executable('fab'),
        '{}:{}'.format(command, ','.join(server_options))
    ])
    subproc = subprocess.Popen(
        shell_args,
        stderr=subprocess.STDOUT,
        stdout=output,
        preexec_fn=os.setsid,
    )
    return subproc, log_file


class RunServerTask(Task):
    """Start an instance of the server using the Flask test web server."""

    name = 'runserver'

    def __init__(self, app_factory, configuration_path):
        """Creates the task.

        app_factory is a callable that returns the Flask app.
        configruation_path is the location of the home directory for the service container's configuration.
        """
        self.app_factory = app_factory
        self.configuration_path = configuration_path

    def run(self, debug_mode=True, port=constants.LOCAL_RUN_PORT, services_profile=None):
        """Called by Fabric when the task is run.
        """
        os.environ['SERVICES_CONFIG_HOME'] = self.configuration_path
        if services_profile:
            os.environ['SERVICES_PROFILE'] = services_profile
        app = self.app_factory('default')
        if isinstance(debug_mode, str):
            debug_mode = (debug_mode.lower() == 'true')
        app.run('0.0.0.0', port=int(port), debug=debug_mode, threaded=False)


class TestTask(Task):
    def run_tests(self, options, additional_options=None, test_config='local.ini'):
        local('export TEST_CONFIG={test_config}; nosetests '.format(test_config=test_config) +
              (additional_options or '') + ' ' + ' '.join(options))

    def test_requirements(self):
        needed = set()
        for requirements_file in constants.REQUIREMENTS_FILES:
            required = set(
                r.req for r in pip.req.parse_requirements(requirements_file))
            installed = set(
                d.as_requirement() for d in pip.get_installed_distributions())
            needed = needed.union(required - installed)
        if needed:
            raise Exception('Required packages not installed %s' % needed)


class TestIntegrationTask(TestTask):
    """Start a test server and run integration tests"""

    name = 'test_integration'

    def __init__(self, port=5000):
        """Creates the task. Specify the local port on which the server will listen."""
        super(TestIntegrationTask, self).__init__()
        self.port = port

    def run(self, test_config='local.ini', run_server=True, nose_options=None, services_profile=None):
        """Called by Fabric when the task is run. Parameters are:

        test_config - The configuration file specifying the local test environment.
        run_server - Controls whether the server is started in a separate process.
        nose_options - Options passed to the Nose test runner.
        services_profile - Service container configuration profile.
        """
        self.test_requirements()

        run_options = [
            '--tests {0}'.format(constants.INTEGRATION_TEST_PATH),
        ]

        running_server = None
        try:
            temp_dir = tempfile.mkdtemp()

            if run_server:
                running_server, _ = _run_server(temp_dir,
                                                constants.RUNSERVER_TASK,
                                                self.port,
                                                services_profile=services_profile)
                TestIntegrationTask.wait_for_port('127.0.0.1', self.port)

            self.run_tests(run_options, nose_options, test_config=test_config)
        finally:
            if running_server is not None:
                os.killpg(running_server.pid, signal.SIGTERM)
            shutil.rmtree(temp_dir)

    @staticmethod
    def wait_for_port(host, port, timeout_ms=10000):
        "Keep connecting to the port until it succeeds or times out."
        print("Waiting for server on port {0}:{1} ".format(host, port))
        iterations = int(timeout_ms / 0.1)
        for _ in range(iterations):
            sys.stdout.write('/')  # / instead of . to distinguish from test
            sys.stdout.flush()
            s = socket.socket()
            if s.connect_ex((host, port)) == 0:
                break
            time.sleep(0.1)
        else:
            print("Couldn't connect to '{0}:{1}'. Aborting.".format(host, port))
            sys.exit(1)
        # Make sure the socket that actually connected gets shut down and
        # closed. Not sending the shutdown seems to leave the server
        # hanging and the tests won't run.
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        print(" '{0}:{1}' ready".format(host, port))


class TestUnitsTask(TestTask):
    """Run unit tests with coverage analysis."""

    name = 'test_units'

    def __init__(self, app_package_name, coverage_options=None):
        """Creates the task.

        app_package_name must be the name of the top-level Python package.

        Use coverage_options to pass options to overide the coverage options
        passed to the Nose test runner.
        """
        super(TestUnitsTask, self).__init__()
        self.app_package_name = app_package_name

        if coverage_options is None:
            self.coverage_options = [
                '--with-coverage',
                '--cover-package={0}'.format(self.app_package_name),
                '--cover-branches',
                '--cover-html',
                '--cover-html-dir={0}'.format(os.path.join(constants.TEST_RESULTS_DIRECTORY, 'coverage')),
                '--exclude-dir=tasks',
            ]
        else:
            self.coverage_options = coverage_options

    def run(self, nose_options=None):
        """Called by Fabric when the task is run. Use nose_options to pass optional
        parameters to the Nose test runner.
        """
        self.test_requirements()
        # run_options = [
        #     '--tests={0}'.format(constants.UNIT_TEST_PATH),
        # ] + self.coverage_options
        run_options = self.coverage_options
        self.run_tests(run_options, additional_options=nose_options)
