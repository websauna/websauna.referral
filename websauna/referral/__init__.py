"""websauna.referral library initialization code."""
import logging
import pyramid
from websauna.system.admin import Admin

from sqlalchemy.ext.declarative import instrument_declarative

from websauna.system.model import Base

from . import models


logger = logging.getLogger(__name__)


def instrument_models(config):
    """Configure concrete model to be included within the host application.

    Defer ``@declared_attr`` resolution until we have Pyramid configuration available.

    This resolves the references to the user model and runs all decorations on the model implementations.
    You must call this before the host application calls ``Base
    """

    # Resolve @declared attr on Referral model
    instrument_declarative(models.ReferralProgram, Base._decl_class_registry, Base.metadata)
    instrument_declarative(models.Conversion, Base._decl_class_registry, Base.metadata)


def includeme(config):
    """Include websauna.referrals in your production.
    """

    config.add_tween("websauna.referral.tweens.ReferralCookieTweenFactory", over=pyramid.tweens.MAIN)

    # Setup database models
    from . import admin
    _admin = Admin.get_admin(config.registry)
    _admin.scan(config, admin)

    from . import adminviews
    config.scan(adminviews)

    # Register event handlers
    from . import subscribers
    config.scan(subscribers)




