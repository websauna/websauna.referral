from pyramid.events import subscriber
from pyramid_web20.system.user.events import FirstLogin

from . import models


@subscriber(FirstLogin)
def convert_user(event):
    request = event.request
    user = event.user
    assert user.id

    session_data = request.session.get("referral")
    models.Conversion.create_conversion(user, session_data)
