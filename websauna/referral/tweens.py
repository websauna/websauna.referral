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

    def is_session_applicable(self, request, response) -> bool:
        """Should we set a session cookie for this request.

        Session cookie should not be set on static resources as this will prevent the HTTP response cacheability.

        We do not want to set session cookie for static resources, as the session cookie either prevents caching of the resources or caching them will cause sessions of different users to mix up. This is because upstream caches do not cache HTTP response content, but the whole HTTP responses, including headers and Set-Cookie header for the session.

        We detect static resources by checking the response content type. The assumption is that anything else than text/html could be static and we do not want to do any session manipulation on those responses.
        """
        return response.content_type == "text/html"

    def __call__(self, request):

        response = self.handler(request)

        if request.method == "GET" and self.is_session_applicable(request, response):

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

        return response


