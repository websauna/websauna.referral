import random
import string
from websauna.system.model import utc
from websauna.system.model import now
from websauna.system.model import DBSession
from sqlalchemy import (
    Column,
    Index,
    Integer,
    String, DateTime, ForeignKey)
from sqlalchemy import Enum

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, backref

SLUG_CHARS = string.ascii_letters + string.ascii_letters.upper() + string.digits


def _generate_slug():
    for attempt in range(0, 100):
        slug = "".join([random.choice(SLUG_CHARS) for i in range(6)])
        existing = DBSession.query(ReferralProgram).filter_by(slug=slug).first()
        if not existing:
            break
    else:
        raise RuntimeError("Could not generate a random slug for shortened URL.")

    return slug



class ReferralProgram:
    """A referral program.

    A referral program can by set by the system (owned by nobody) or created by some site user. For the user created referral programs there is usually some incentive like get free Apple Watch if you tell about this website to your 20 friends.

    Each referral program gets its own slug which is a HTTP GET query parameter attached to incoming links. When the a visitor lands on the site through one of these links, the viistor is marked with a permacookie to belonging to the referral program. If this visitor ever converts to user, i.e. signs up, the referral program owner can be credited for bringing in a new user.

    System set referral programs are good for tracking your advertisement links internally.

    """
    __tablename__ = 'referral_program'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), default="")

    #: Internal is an affiliate program created through site admin
    #: Referral is "share to your friends" type of program
    #: Affiliate is revenue sharing program as a self-subscription service
    program_type = Column(Enum('internal', 'referral', 'affiliate', name="referral_program_type"), default="referral")

    created_at = Column(DateTime(timezone=utc), default=now)
    updated_at = Column(DateTime(timezone=utc), onupdate=now)
    expires_at = Column(DateTime(timezone=utc), nullable=True, default=None)

    slug = Column(String(6), unique=True, default=_generate_slug)
    hits = Column(Integer, default=0)

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @declared_attr
    def owner(cls):
        """The owner of this referral program.

        If you do not like the default implementation, you can subclass ReferralProgram and then override ``owner`` and ``owner_id`` SQLALchemy declared attributes. Then you call ``instrument_declarative()`` to your custom model implementation, instead of the default ``ReferralProgram``.
        """
        from websauna.system.user.utils import get_user_class
        config = cls.metadata.pyramid_config
        User = get_user_class(config.registry)
        return relationship(User, backref="referral_programs")

    @declared_attr
    def owner_id(cls):
        from websauna.system.user.utils import get_user_class
        config = cls.metadata.pyramid_config
        User = get_user_class(config.registry)
        return Column(Integer, ForeignKey('{}.id'.format(User.__tablename__)))

    def get_converted_count(self):
        """How many of the users who arrived through this referral program signed up."""
        return DBSession.query(Conversion).filter_by(referral_program=self).count()


class Conversion:
    """User who signed up through referral."""

    __tablename__ = 'referral_conversion'

    id = Column(Integer, primary_key=True)
    referral_program_id = Column(Integer, ForeignKey('referral_program.id'), nullable=True)
    referral_program = relationship(ReferralProgram, backref="conversions")

    #: If this affiliate is paid one, when this lead was credited to our affiliate partner
    paid_at = Column(DateTime(timezone=utc), nullable=True, default=None)

    #: The url where we captured this visitor initially
    referrer = Column(String(512))

    @declared_attr
    def user_id(cls):
        """Foreign key to the users table."""
        from websauna.system.user.utils import get_user_class
        config = cls.metadata.pyramid_config
        User = get_user_class(config.registry)
        return Column(Integer, ForeignKey('{}.id'.format(User.__tablename__)), nullable=False, unique=True)

    @declared_attr
    def user(cls):
        """The user who was converted."""
        from websauna.system.user.utils import get_user_class
        config = cls.metadata.pyramid_config
        User = get_user_class(config.registry)
        return relationship(User, foreign_keys=[Conversion.user_id], backref=backref("conversion", uselist=False))

    @classmethod
    def is_converted(cls, user):
        """Make sure the user do not get two conversions."""
        return DBSession.query(Conversion).filter(Conversion.user_id == user.id).first() is not None

    @classmethod
    def create_conversion(cls, user, session_data):
        """Mark signed up user to have arrived from certain referral program.

        :param session_data: Referral session data from the initial visitor catpure

        :return: Created Conversion entry or none if referral data is empty or invalid
        """

        assert user, "No user"
        assert user.id, "Not a valid user"

        if not session_data:
            return None

        ref = session_data["ref"]
        if ref:
            program = DBSession.query(ReferralProgram).filter_by(slug=ref).first()
        else:
            program = None

        c = Conversion()

        # XXX: test_conversion_admin fails inside transaction machinery if this is set by using relationship(). One must do forced id set here. No idea why.
        c.user_id = user.id
        c.referral_program = program

        # Can be None too
        referrer = session_data["referrer"]
        if referrer:
            c.referrer = referrer[0:511]
        else:
            c.referrer = None

        DBSession.add(c)
        return c




#: For quick resolution if referrals
Index('referral_program_slug_index', ReferralProgram.slug, unique=True)