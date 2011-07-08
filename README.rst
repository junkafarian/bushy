Bushy
=====

A git workflow plugin inspired by 
`git-pivotal <https://github.com/trydionel/git-pivotal>`_ but intending to
support multiple project management platforms aside from just Pivotal Tracker.


Installation
============

Bushy is a `Python <http://www.python.org>`_ package and can be installed using
the ``easy_install`` or ``pip`` commands. For the most seamless integration
install the package so the generated console scripts are available in your $PATH.

It is always advisable to install python packages within a virtualenv. If you
``activate`` your project virtualenv while developing, this will place the
commands in your $PATH automatically. Alternatively, you can create a dedicated
virtualenv for Bushy and add the scripts to your shell config. If you use
``bash`` you could do the following to ensure the commands are accessible::

    $ virtualenv-2.6 --no-site-packages bushy
    $ bushy/bin/pip install bushy
    $ echo "export PATH = $PATH:/path/to/bushy/bin" > ~/.bash_profile

This will allow you to run the following commands::

    $ git feature
    $ git finish
    $ git bug
            
As well as::

    $ /path/to/bushy/bin/git-feature
    $ /path/to/bushy/bin/git-finish
    $ /path/to/bushy/bin/git-bug


Usage
=====

Pivotal Configuration
---------------------

Bushy requires global and project local configuration to integrate fully.

Required local configuration (from within your project directory)::

    $ git config -f .git/config bushy.platform pivotal # use Pivotal Tracker for this project
    $ git config -f .git/config bushy-pivotal.project-id PROJECT_ID # from the project url on the Pivotal Tracker site

Required global configuration::

    $ git config --global bushy-pivotal.api-token TOKEN # taken from the profile section on the Pivotal Tracker site
    $ git config --global bushy-pivotal.full-name "YOUR NAME"

Optional configuration::

    $ git config --global bushy-pivotal.integration-branch # the name of the integration branch if different from master
    $ git config --global bushy-pivotal.only-mine # only select from new features that are assigned to you


Working on a new feature
------------------------

You can select a new feature to work on using the ``git-feature`` command::

    junkafarian$ git feature
    Retrieving latest features from Pivotal Tracker
    Story: hook up with pivotal
    URL: http://www.pivotaltracker.com/story/show/8236507
    Updating feature status in Pivotal Tracker...
    Enter branch name (will be prepended by 8236507) [feature]: 
    Switching to branch 8236507-feature
    junkafarian$

If you want to work on a specific story you can specify the story id::

    junkafarian$ git feature -s 12345
    Retrieving story 12345 from Pivotal Tracker
    Story: hook up with pivotal
    URL: http://www.pivotaltracker.com/story/show/12345
    Updating feature status in Pivotal Tracker...
    Enter branch name (will be prepended by 12345) [feature]: 
    Switching to branch 12345-feature
    junkafarian$

This will switch you to a new branch for working on the issue
selected.

Once you have completed the development work / checked tests pass /
committed the changes, you can declare the task as finished::

    junkafarian$ git finish
    Marking Story 8236507 as finished...
    Merging 8236507-feature into master
    Removing 8236507-feature branch
    Merged code into trunk. Please push upstream and notify the release manager if necessary
    junkafarian$

You can then push these changes upstream.

Roadmap
=======

* Unit Tests - completed
* Allow features / bugs to be selected by ID on the commandline - completed
* Support for github issues


Etymology
=========

``Bushy`` encourages a workflow based entirely around code branches.
Bushes have lots of branches... 
