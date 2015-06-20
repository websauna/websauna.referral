import socket
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.events import BeforeRender
from pyramid.settings import asbool
from pyramid_deform import configure_zpt_renderer

import websauna.system
import websauna.system.user.views as user_views
from websauna.system.admin import Admin
from websauna.utils.configincluder import IncludeAwareConfigParser

from sqlalchemy.orm.exc import DetachedInstanceError


class Initializer(websauna.system.Initializer):
    """An initialization configuration used when testing websauna.referral."""

    def configure_instrumented_models(self, settings):
        super(Initializer, self).configure_instrumented_models(settings)

        # Delayed @declared_attr resolution
        from websauna.referral import instrument_models
        instrument_models(self.config)

    def run(self, settings):
        super(Initializer, self).run(settings)
        from websauna.referral import includeme
        includeme(self.config)


def main(global_config, **settings):
    settings = IncludeAwareConfigParser.retrofit_settings(global_config)
    init = Initializer(global_config, settings)
    init.run(settings)
    return init.make_wsgi_app()
