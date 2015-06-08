websauna.referral
=====================

*websauna.referral* is a *websauna* plugin to expand your site with referrals and affiliate functionality.

Features
--------

* System-created or user created referral programs

* All who have admin view access can shorten URLs

* Count hits per URL

Configuration
-------------

``websauna.referral.permacookie``: name of the cookie used to track incoming users

Installation
------------

Limitations
-----------

The referrer data is stored in the session. If the session expires or the user clears cookies, the referrer information is lost.

Development and tests
-----------------------

To run development server::

     ws-sync-db development.ini
     pserve development.ini --reload

To run tests::

     py.test websauna/referral -s --splinter-webdriver=firefox --splinter-make-screenshot-on-failure=false --ini=test.ini


