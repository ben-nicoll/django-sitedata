from django.conf import settings

from sitedata.middleware import SiteData, SiteDataMiddleware


def test_sitedata_middleware(rf):
    """
    Validate that SiteDataMiddleware attaches to request, has attribute 'name' which matches
    settings, and the middleware is loaded in settings.
    """
    request = rf.get('/')
    SiteDataMiddleware().process_request(request)
    assert 'sitedata.middleware.SiteDataMiddleware' in settings.MIDDLEWARE
    assert request.sitedata.name == settings.SITEDATA[settings.SITEDATA_DEFAULT]['name']


def test_sitedata_local(rf):
    """
    Validate that LOCAL.sitedata is populated correctly by the middleware
    FIXME: Don't assume StocksDigital SITEDATA is valid in settings; populate and test explicit dummy data
    """
    site_ch = SiteData(label='catalysthunter')
    site_nmb = SiteData(label='nextminingboom')

    request = rf.get('/', HTTP_HOST=site_ch.hostname)
    SiteDataMiddleware().process_request(request)
    from sitedata import LOCAL
    assert LOCAL.sitedata.label == site_ch.label

    request = rf.get('/', HTTP_HOST=site_nmb.hostname)
    SiteDataMiddleware().process_request(request)
    from sitedata import LOCAL
    assert LOCAL.sitedata.label == site_nmb.label
