from pyramid.events import subscriber

from websauna.system.user.events import FirstLogin
from websauna.system.model import DBSession

from . import models


@subscriber(FirstLogin)
def convert_user(event):
    request = event.request
    user = event.user
    assert user.id

    # FirstLogin event may occur in non-sync manner regarding conversion tracking if the users are batch created or created outside the standard sign up flow. In this case we could get two conversions per user which we cannot handle.
    if not models.Conversion.is_converted(user):
        session_data = request.session.get("referral")
        c = models.Conversion.create_conversion(user, session_data)
