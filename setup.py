from setuptools import setup
from pip import req


def parse_requirements(filename):
    return [str(ir.req) for ir in req.parse_requirements(filename, session=False)]

__version__ = __import__('quizlet').__version__

setup(
    name='Quizlet API',
    version='0.1',
    author='Aliaksei Sukharevich',
    author_email='suharevichalexey@gmail.com',
    description='Python wrapper for Quizlet HTTP API.',
    packages=['quizlet'],
    install_requires=parse_requirements('requirements.txt'),
    tests_require=parse_requirements('requirements-test.txt'),
    test_suite="tests",
)
