import os
from setuptools import find_packages
from distutils.core import setup

REQUIRES = [
    'pivotal-py',
    'httplib2',
    ]

setup(
    name='bushy',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    version='0.2',
    author='junkafarian',
    install_requires=REQUIRES,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Software Development",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Bug Tracking",
        "Topic :: Utilities",
        "Environment :: Console",
    ],
    description='',
    long_description=open(os.path.join(os.path.dirname(__file__), "README.rst")).read(),
    entry_points='''
[console_scripts]
git-feature = bushy.scripts:feature
git-bug = bushy.scripts:bug
git-finish = bushy.scripts:finish
''',
    )
