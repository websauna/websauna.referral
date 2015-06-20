from urllib.parse import urlencode
from pyramid.httpexceptions import HTTPTemporaryRedirect

from . import config
from . import models
from websauna.system.model import DBSession


class ReferralCookieTweenFactory:
    """Tween to capture referral links and """
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):

        if request.method == "GET":
            # We are only interested in incoming links with a referrer
            q_name = config.get_query_parameter_name(self.registry)
            ref = request.GET.get(q_name, None)

        # We capture only the first referrer
            if not "referral" in request.session:
                request.session["referral"] = {
                    "ref": ref,
                    "referrer": request.referrer or None,
                }

                # Increase referral hit count
                if ref:
                    program = DBSession.query(models.ReferralProgram).filter_by(slug=ref).first()
                    if program:
                        program.hits += 1

                    # Strip referer parameter from the query string, redirect user to the site.
                    # This possible mixes the order of the query string parameter, but we don't care about that now.
                    q_params = {key: value for key, value in request.GET.items() if key != q_name}

                    if q_params:
                        reconstructed_query_string = "?" + urlencode(q_params)
                    else:
                        reconstructed_query_string = ""
                    url = request.host_url + request.path + reconstructed_query_string
                    return HTTPTemporaryRedirect(url)

        response = self.handler(request)
        return response


