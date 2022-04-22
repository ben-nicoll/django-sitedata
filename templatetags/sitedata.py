"""
Template tags/filters for 'relative' URL's (i.e. from get_absolute_url, url name, etc) that return with FQDN.
"""
from django import template
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.defaulttags import URLNode, url
from django.urls import NoReverseMatch, reverse
from django.utils.encoding import force_str
from django.utils.html import conditional_escape

from sitedata.utils import SiteData

register = template.Library()


def get_host_scheme_from_context(context):
    """Returns (hostname, scheme) from context"""
    if 'request' in context:
        sitedata = context['request'].sitedata
        return sitedata.get_host(), sitedata.scheme
    else:
        # No request context, fallback to default SiteData label.
        sitedata = SiteData()
        return sitedata.get_host(), sitedata.scheme


class SiteDataURLNode(URLNode):
    """
    Reimplements Django's URLNode, but returns with full FQDN, and allows fetching for a specific SiteData label
    """

    def render(self, context):
        """
        Overrides render() method to return with FQDN from request context or optional sitedata parameter.
        Internals here are very similar to URLNode.render internals, but supports reverse(urlconf).
        """
        args = [arg.resolve(context) for arg in self.args]
        kwargs = {
            force_text(k, 'ascii'): v.resolve(context)
            for k, v in self.kwargs.items()
        }

        view_name = self.view_name.resolve(context)

        try:
            sitedata = SiteData(label=kwargs.pop('sitedata'))
            urlconf = sitedata.urlconf
        except (AttributeError, KeyError):
            (sitedata, urlconf) = None, None

        try:
            current_app = context.request.current_app
        except AttributeError:
            try:
                current_app = context.request.resolver_match.namespace
            except AttributeError:
                current_app = None

        # Try to look up the URL. If it fails, raise NoReverseMatch unless the
        # {% url ... as var %} construct is used, in which case return nothing.
        # urlconf parameter is used here (not implemented in original URLNode.re render)
        url = ''
        try:
            url = reverse(view_name, urlconf=urlconf, args=args, kwargs=kwargs, current_app=current_app)
        except NoReverseMatch:
            if self.asvar is None:
                raise

        if context.autoescape:
            url = conditional_escape(url)

        if sitedata:
            (hostname, scheme) = sitedata.get_host(), sitedata.scheme
        else:
            # Assign based on the current request context
            (hostname, scheme) = get_host_scheme_from_context(context)

        fqdn_url = fqdn_format(scheme, hostname, url)

        if self.asvar:
            context[self.asvar] = fqdn_url
            return ''
        else:
            return fqdn_url


@register.tag
def url_fqdn(parser, token):
    """
    Acts like 'url(), but returns with FQDN of current context.  Takes optional 'sitedata' label to override.

    Use like the following:
    {% url_fqdn 'name-of-url' %}
    {% url_fqdn 'name-of-url' sitedata='djangohunter' %}
    """

    node = url(parser, token)

    return SiteDataURLNode(
        view_name=node.view_name,
        args=node.args,
        kwargs=node.kwargs,
        asvar=node.asvar,
    )


def fqdn_format(scheme, hostname, path):
    """
    Returns a FQDN from a supplied scheme, hostname, path
    """
    if '//' in path:
        return path
    else:
        if not path.startswith('/'):
            path = '/' + path

        return '{scheme}://{hostname}{path}'.format(
            scheme=scheme,
            hostname=hostname,
            path=path
        )


@register.simple_tag(takes_context=True)
def with_fqdn(context, path):
    """
    Takes a URL string and returns it with FQDN
    """
    (hostname, scheme) = get_host_scheme_from_context(context)
    return fqdn_format(scheme, hostname, path)


@register.simple_tag(takes_context=True)
def static_with_fqdn(context, asset_path):
    """
    Get an static URL with the FQDN from the asset path
    """
    path = static(asset_path)
    (hostname, scheme) = get_host_scheme_from_context(context)
    return fqdn_format(scheme, hostname, path)


@register.simple_tag(takes_context=True)
def sitedata_title(context, title):
    """
    Returns 'title' text with the specified SiteData formatting.  Used to add prefixes/suffixes for the page title.
    """
    return context['request'].sitedata.get_title(title)
