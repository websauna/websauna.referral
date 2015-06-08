import time
from pyramid_web20 import DBSession
from pyramid_web20.tests.utils import create_user, EMAIL, PASSWORD
import transaction

from websauna.referral import models


def create_program(session):
    r = models.ReferralProgram()
    session.add(r)
    return r


def test_process_ref_tag(browser, web_server, dbsession, app):
    """Referral program permacookie is set on the user if he/she arrives from referral program link.."""
    with transaction.manager:
        r = create_program(dbsession)
        dbsession.flush()
        slug = r.slug
        assert slug

    b = browser
    b.visit("{}/?ref={}".format(web_server, slug))

    time.sleep(1)

    # Assume we land on the home page, referrer tag stripped away
    assert b.url.strip("/") == web_server.strip("/")


def test_multiple_query_parameters(browser, web_server, dbsession, app):
    """Referral query parameter removing code should not touch other query parameters."""
    with transaction.manager:
        r = create_program(dbsession)
        dbsession.flush()
        slug = r.slug

    b = browser
    b.visit("{}/?foo=bar&blarg=faa&ref={}".format(web_server, slug))

    time.sleep(1)

    # The order of query string parameters is not stable as it goes through non-ordered dictionary
    assert str(b.url) in (web_server + "/?foo=bar&blarg=faa", web_server + "/?blarg=faa&foo=bar")





