import os
from setuptools import find_packages
from distutils.core import setup

REQUIRES = [
    'httplib2',
    'pivotal-py>=0.1.2',
    ]

setup(
    name='bushy',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    version='0.3dev',
    author='junkafarian',
    author_email='junkafarian@gmail.com',
    url='https://github.com/junkafarian/bushy',
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
    description='A git workflow plugin.',
    long_description=open('README.rst').read() + open('CHANGES.rst').read(),
    include_package_data=True,
    entry_points='''
[console_scripts]
git-feature = bushy.scripts:feature
git-bug = bushy.scripts:bug
git-finish = bushy.scripts:finish
''',
    )
