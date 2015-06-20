import time
from websauna.system.model import DBSession
from websauna.tests.utils import create_user, EMAIL, PASSWORD, get_user
import transaction

from websauna.referral import models


def create_program(session, user=None):
    r = models.ReferralProgram()
    if user:
        r.owner = user
    session.add(r)
    return r


def register(browser, web_server):

    b = browser

    b.click_link_by_text("Sign up")

    assert b.is_element_visible_by_css("#sign-up-form")

    b.fill("email", EMAIL)
    b.fill("password", PASSWORD)
    b.fill("password-confirm", PASSWORD)

    b.find_by_name("submit").click()

    assert b.is_element_visible_by_css("#waiting-for-activation")

    # Now peek the Activation link from the database
    user = get_user()
    assert user.activation.code

    activation_link = "{}/activate/{}/{}".format(web_server, user.id, user.activation.code)

    b.visit(activation_link)

    assert b.is_element_visible_by_css("#sign-up-complete")

    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("Log_in").click()


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

    # See that we have increased the hit count
    with transaction.manager:
        r = DBSession.query(models.ReferralProgram).filter_by(slug=slug).first()
        assert r.hits == 1


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



def test_convert(browser, web_server, dbsession):
    """Referral program permacookie is set on the user if he/she arrives from referral program link.."""
    with transaction.manager:
        r = create_program(dbsession)
        dbsession.flush()
        slug = r.slug
        assert slug

    b = browser
    b.visit("{}/?ref={}".format(web_server, slug))

    register(browser, web_server)

    # Check we got some conversion
    with transaction.manager:
        r = DBSession.query(models.ReferralProgram).filter_by(slug=slug).first()
        assert r.hits == 1
        assert r.get_converted_count() == 1


def test_blank_user_sign_up(browser, web_server, dbsession):
    """See that including referral tweens do not break ordinate sign up process."""
    browser.visit(web_server)
    register(browser, web_server)


def test_referral_admin(browser, web_server, dbsession):
    """Admin interface allows us to add and list referrals."""

    with transaction.manager:
        u = create_user(admin=True)

    b = browser
    b.visit(web_server + "/login")

    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("Log_in").click()

    assert b.is_element_visible_by_css("#nav-admin")

    b.visit(web_server + "/admin/referrals/add")

    b.fill("name", "foobar")
    b.find_by_name("add").click()

    assert b.is_text_present("Slug")

    with transaction.manager:
        r = DBSession.query(models.ReferralProgram).first()
        slug = r.slug

    # See the listing does not broken out
    b.visit(web_server + "/admin/referrals/listing")

    assert b.is_text_present(slug)


def test_conversion_admin(browser, web_server, dbsession):
    """Admin interface allows us to add and list referrals."""

    with transaction.manager:
        r = create_program(dbsession)
        u = create_user(admin=True)
        models.Conversion.create_conversion(u, dict(referrer="http://foo.bar", ref=r.slug))


    b = browser
    b.visit(web_server + "/login")

    b.fill("username", EMAIL)
    b.fill("password", PASSWORD)
    b.find_by_name("Log_in").click()

    b.visit(web_server + "/admin/conversions/listing")

    # Conversion source is visible in the listing
    assert b.is_text_present("http://foo.bar")

    # We should not be able to edit conversions
    assert not b.is_text_present("Edit")


def test_program_owner(dbsession):
    """Programs owner is recoreded correctly."""

    with transaction.manager:
        u = create_user(admin=True)
        r = create_program(dbsession, user=u)

    with transaction.manager:
        r = DBSession.query(models.ReferralProgram).first()
        u = get_user()
        assert r.owner == u

