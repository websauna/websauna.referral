"""URL shortening views."""
import logging

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid_deform import CSRFSchema
from pyramid_layout.panel import panel_config
from pyramid_web20 import DBSession
from pyramid_web20.system.core import messages
from pyramid_web20.system.admin import views as adminviews
from pyramid_web20.system.crud import listing

import colander
import deform

from . import models
from .admin import ReferralProgramAdmin
from websauna.viewconfig import view_overrides


logger = logging.getLogger(__name__)


class ReferralProgramSchema(CSRFSchema):
    """A form to allow entering URL for shortening."""

    #: An URL input using HTML5 <input type="url">
    url = colander.SchemaNode(
        colander.String(),
        title='URL',
        validator=colander.url,
        widget=deform.widget.TextInputWidget(size=40, maxlength=512, template='url'))


@view_overrides(context=ReferralProgramAdmin)
class ReferralProgramAdd(adminviews.Add):
    """Admin view for editing shortened URL."""

    includes = [
        "name"
    ]




@view_overrides(context=ReferralProgramAdmin.Resource)
class ReferralProgramShow(adminviews.Show):
    """Admin view for showing shortened URL."""

    #: Define what views we will show (deform readonly mode)
    includes = ["id", "created_at", "owner", "slug", "url", "hits"]


@view_overrides(context=ReferralProgramAdmin.Resource)
class ReferralProgramEdit(adminviews.Edit):
    """Admin view for editing shortened URL."""

    includes = [
        "url",
        "slug"
    ]

@view_overrides(context=ReferralProgramAdmin)
class ReferralProgramLListing(adminviews.Listing):
    """Listing view for shortened URLs."""

    table = listing.Table(
        columns = [
            listing.Column("id", "Id",),
            listing.Column("slug", "Slug"),
            listing.Column("owner", "Owner"),
            listing.Column("hits", "Hits"),
            listing.ControlsColumn()
        ]
    )