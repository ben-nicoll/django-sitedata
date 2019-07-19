import weakref

from django.conf import settings
from django.core.exceptions import DisallowedHost
from django.http.request import split_domain_port, validate_host
from django.utils.deprecation import MiddlewareMixin

from sitedata import LOCAL
from sitedata.utils import SiteData


class SiteDataMiddleware(MiddlewareMixin):
    """
    Middleware which provides request.sitedata, which holds "current site" specific metadata - used for
    multi-tenant Django applications where we need to dynamically populate data specific to a site.

    request.sitedata is an instance of sitedata.utils.SiteData, which looks up the canonical domain for
    the current request hostname.
    """

    def process_request(self, request):
        host = request.get_host().lower()
        hostname, port = split_domain_port(host)

        if not hostname:
            raise DisallowedHost('Invalid hostname in HTTP request')

        require_exact_match = getattr(settings, 'SITEDATA_MIDDLEWARE_REQUIRE_EXACT_HOSTNAME', False)

        if validate_host(hostname, settings.ALLOWED_HOSTS):
            request.sitedata = SiteData(hostname=hostname, require_exact_match=require_exact_match)
            LOCAL.sitedata_ref = weakref.ref(request.sitedata)  # allow sitedata to be accessed from LOCAL

        # overrides request.urlconf if specified
        if hasattr(request.sitedata, 'urlconf') and request.sitedata.urlconf is not settings.ROOT_URLCONF:
            request.urlconf = request.sitedata.urlconf

        # Monkey patches request._get_scheme() to return 'https' instead of 'http'
        if hasattr(request.sitedata, 'scheme') and request.sitedata.exact_match_found \
                and request.sitedata.scheme is 'https':
            request._get_scheme = _get_scheme_https


def _get_scheme_https():
    return 'https'
