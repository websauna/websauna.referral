"""URL shortening views."""
import logging

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid_deform import CSRFSchema
from pyramid_layout.panel import panel_config
from websauna.system.model import DBSession
from websauna.system.core import messages
from websauna.system.admin import views as adminviews, Admin
from websauna.system.crud import listing

import colander
import deform

from . import models
from .admin import ReferralProgramAdmin, ConversionAdmin
from websauna.viewconfig import view_overrides


logger = logging.getLogger(__name__)


@view_overrides(context=ReferralProgramAdmin)
class ReferralProgramAdd(adminviews.Add):
    """Admin view for editing shortened URL."""

    # We only ask for name field, everything else is filled by system
    includes = [
        "name"
    ]

    def create_object(self):
        """When created through admin, all referral programs are internal type by default."""
        model = self.get_model()
        item = model()
        item.program_type = "internal"
        return item



@view_overrides(context=ReferralProgramAdmin.Resource)
class ReferralProgramShow(adminviews.Show):
    """Admin view for showing shortened URL."""

    #: Define what views we will show (deform readonly mode)
    includes = ["id", "program_type", "created_at", "slug", "url", "hits"]


@view_overrides(context=ReferralProgramAdmin.Resource)
class ReferralProgramEdit(adminviews.Edit):
    """Admin view for editing shortened URL."""

    includes = [
        "url",
        "slug",
        "program_type"
    ]


def get_user_url(request, resource):
    obj = resource.get_object()
    user = obj.user
    admin = Admin.get_admin(request.registry)
    return admin.get_admin_object_url(request, user, "show")


def get_owner_url(request, resource):
    obj = resource.get_object()
    user = obj.owner
    if user:
        admin = Admin.get_admin(request.registry)
        return admin.get_admin_object_url(request, user, "show")
    else:
        return None


@view_overrides(context=ReferralProgramAdmin)
class ReferralProgramListing(adminviews.Listing):
    """Listing view for shortened URLs."""

    table = listing.Table(
        columns=[
            listing.Column("id", "Id",),
            listing.Column("name", "Name"),
            listing.Column("slug", "Slug"),
            listing.Column("owner", "Owner", getter=lambda obj: obj.owner and obj.owner.friendly_name or "", navigate_url_getter=get_owner_url),
            listing.Column("hits", "Hits"),
            listing.Column("converted", "Converted", getter=lambda obj: obj.get_converted_count()),
            listing.ControlsColumn()
        ]
    )


def get_referral_program_url(request, resource):
    obj = resource.get_object()
    r = obj.referral_program
    if not r:
        return None
    admin = Admin.get_admin(request.registry)
    return admin.get_admin_object_url(request, r, "show")



@view_overrides(context=ConversionAdmin)
class ConversionListing(adminviews.Listing):
    """Listing view for shortened URLs."""

    table = listing.Table(
        columns=[
            listing.Column("program", "Program", getter=lambda obj: obj.referral_program and obj.referral_program.name or "", navigate_url_getter=get_referral_program_url),
            listing.Column("user", "User", getter=lambda obj: obj.user.friendly_name if obj.user else "", navigate_url_getter=get_user_url),
            listing.Column("referrer", "Referrer"),
            listing.ControlsColumn()
        ]
    )
