from unittest import mock

from django.conf import settings
from django.template import Context, Template

from sitedata.templatetags.sitedata import fqdn_format
from sitedata.utils import SiteData


def test_url_fqdn():
    # Expect a FQDN to work for a given site in context
    template = (
        '{% load sitedata %}'
        '{% url_fqdn "search" %}'
    )
    request = mock.Mock()
    request.sitedata = SiteData(label='nextminingboom')
    rendered = Template(template).render(Context({'request': request}))
    assert rendered == 'http://www.nextminingboom.com/search/'

    # Expect a FQDN stored in an 'as' variable
    template = (
        '{% load sitedata %}'
        '{% url_fqdn "search" as foo %}'
        '{{foo}}'
    )
    request = mock.Mock()
    request.sitedata = SiteData(label='nextminingboom')
    rendered = Template(template).render(Context({'request': request}))
    assert rendered == 'http://www.nextminingboom.com/search/'

    # Expect a FQDN with fallback to the default site when no context
    template = (
        '{% load sitedata %}'
        '{% url_fqdn "search" sitedata="catalysthunter" %}'
    )
    rendered = Template(template).render(Context({}))
    assert rendered == 'http://catalysthunter.com/search/'

    # Expect a FQDN for the site specified in the tag params
    template = (
        '{% load sitedata %}'
        '{% url_fqdn "search" sitedata="nextinvestors" %}'
    )
    request = mock.Mock()
    request.sitedata = SiteData(label='catalysthunter')
    rendered = Template(template).render(Context({'request': request}))
    assert rendered == 'http://www.nextinvestors.com/search/'


def test_with_fqdn():
    # Expect FQDN for paths to work for a given site
    template = (
        '{% load sitedata %}'
        '{% with_fqdn "/foo/bar/" %}'
    )
    request = mock.Mock()
    request.sitedata = SiteData(label='nextminingboom')
    rendered = Template(template).render(Context({'request': request}))
    assert rendered == 'http://www.nextminingboom.com/foo/bar/'

    # Expect FQDN for paths to fallback to the default site
    template = (
        '{% load sitedata %}'
        '{% with_fqdn "/foo/bar/" %}'
    )
    rendered = Template(template).render(Context({}))
    assert rendered == 'http://catalysthunter.com/foo/bar/'

    # Expect FQDN for file paths
    template = (
        '{% load sitedata %}'
        '{% with_fqdn "/foo/bar/baz.jpg" %}'
    )
    rendered = Template(template).render(Context({}))
    assert rendered == 'http://catalysthunter.com/foo/bar/baz.jpg'

    # Expect FQDN for paths with no prefixed '/'
    template = (
        '{% load sitedata %}'
        '{% with_fqdn "foo/bar/" %}'
    )
    rendered = Template(template).render(Context({}))
    assert rendered == 'http://catalysthunter.com/foo/bar/'


def static_with_fqdn():
    """
    Expect the tag to use the default sitedata when no request
    context provided (catalysthunter.com)
    """
    template = (
        '{% load sitedata %}'
        '{% static_with_fqdn path %}'
    )
    asset_path = settings.SITEDATA['catalysthunter']['og_image']['path']
    rendered = Template(template).render(Context({'path': asset_path}))
    assert rendered == 'http://catalysthunter.com/static/{}'.format(asset_path)


def test_sitedata_title():
    template = (
        '{% load sitedata %}'
        '{% sitedata_title "Woo" %}'
    )
    request = mock.Mock()
    request.sitedata = SiteData(label='catalysthunter')
    rendered = Template(template).render(Context({'request': request}))
    assert rendered == request.sitedata.get_title('Woo')


def test_fqdn_format():
    # Normal case
    expected = 'http://example.com/foo/'
    actual = fqdn_format('http', 'example.com', '/foo/')
    assert expected == actual

    # No prefixed slash on path
    expected = 'http://example.com/foo/'
    actual = fqdn_format('http', 'example.com', 'foo/')
    assert expected == actual

    # Only use path if path is a FQDN
    expected = 'http://example.com/foo/'
    actual = fqdn_format('https', 'wrong.net', 'http://example.com/foo/')
    assert expected == actual
