websauna.referral
=====================

*websauna.referral* is a *websauna* addonto expand your site with referrals and affiliate functionality.

Features
--------

* System-created or user created referral programs (affiliates)

* Have statistics how well referral programs are going

* Record HTTP referer for all incoming visitors and converted sign ups

Configuration
-------------

``websauna.referral.query_parameter``: the name of query parameter which tracks the referral program slug. The default is ``ref``.

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


