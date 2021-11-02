from setuptools import setup

with open('requirements.txt') as f:
    install_requires = f.read().strip().split('\n')

__version__ = __import__('quizlet').__version__

setup(
    name='Quizlet API',
    version='0.1',
    author='Aliaksei Sukharevich',
    author_email='suharevichalexey@gmail.com',
    description='Python wrapper for Quizlet HTTP API.',
    packages=['quizlet'],
    install_requires=install_requires,
    tests_require=install_requires,
    test_suite="tests",
)
