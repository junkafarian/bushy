import os
from distutils.core import setup, find_packages

REQUIRES = [
    'pivotal-py',
    ]

setup(
    name='pyvotalgit',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    version='0.0.1',
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
git-feature = pyvotalgit.feature:main
git-bug = pyvotalgit.bug:main
git-chore = pyvotalgit.chore:main
git-finish = pyvotalgit.finish:main
''',
    )
