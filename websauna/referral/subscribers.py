from pyramid_web20.system.user.events import FirstLogin


@subscriber(FirstLogin)
def send_receipt(event):
    request = event.request
    user = event.user
    assert user.id

    permacookei = request.cookies.get("")

    create_conversion()