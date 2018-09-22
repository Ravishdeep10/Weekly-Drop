Weekly-Drop
==========

Web app that tracks new hip hop album releases every week. Using the unique tastes of the /r/hiphopheads subreddit, I used the reddit api to track the hottest albums, singles and extended plays talked about on the subreddit after their initial release. When the website loads it will takes the information from those reddit posts and turn them into a class of spotify objects created using the Spotify Web API and plamere's spotipy python library. The resulting display is an updated selection of albums every Thursday at 9:00 pm pacific time along with a spotify play button in order to start listening to each project. This application was made because as an avid hip hop fan I would wait Thirsday night and scrape reddit to find what the new releases were, but now this application automates this process for me.

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django

.. image:: https://github.com/Ravishdeep10/Weekly-Drop/blob/master/docs/images/Screen_Shot_1_2018_09_20.png
 
.. image:: https://github.com/Ravishdeep10/Weekly-Drop/blob/master/docs/images/Screen_Shot_2_2018_09_20.png

Settings
--------

Moved to settings_.

.. _settings: http://cookiecutter-django.readthedocs.io/en/latest/settings.html

Basic Commands
--------------

Setting Up Your Users
^^^^^^^^^^^^^^^^^^^^^

* To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

* To create an **superuser account**, use this command::

    $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

Type checks
^^^^^^^^^^^

Running type checks with mypy:

::

  $ mypy weekly_drop

Test coverage
^^^^^^^^^^^^^

To run the tests, check your test coverage, and generate an HTML coverage report::

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

Running tests with py.test
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ pytest

Live reloading and Sass CSS compilation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Moved to `Live reloading and SASS compilation`_.

.. _`Live reloading and SASS compilation`: http://cookiecutter-django.readthedocs.io/en/latest/live-reloading-and-sass-compilation.html



