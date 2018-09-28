from fabric.operations import local
from fabric.tasks import Task


class ComplexityTask(Task):
    """Perform code complexity analysis using Radon."""

    name = 'complexity'

    def run(self):
        local('radon cc -a .')


class Flake8Task(Task):
    """Perform code analysis using PEP8 and PyFlakes."""

    name = 'flake8'

    def run(self):
        local('flake8 --max-line-length=120 --count .')
