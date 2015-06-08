


def get_permacookie_name(registry):
    return registry.settings.get("websauna.referrals.permancookie") or "refcookie"


def get_query_parameter_name(registry):
    return registry.settings.get("websauna.referrals.query_parameter") or "ref"
