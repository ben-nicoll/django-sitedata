"""
Provides decorators to run sections of tests multiple times with different hosts
"""
from functools import wraps

from django.test.client import Client, RequestFactory

from sitedata.utils import SiteData


def sitedata(site):
    """
    Use as a decorator on a pytest function which uses 'rf' or 'client', to automatically request correct hostname.

    Use like the following:
    @sitedata('catalysthunter')

    If you want to get the current sitedata inside of a test:
    print(client.sitedata.label)
    """

    def real_decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            args, kwargs = _sitedata_monkeypatch(site, *args, **kwargs)
            function(*args, **kwargs)

        return wrapper

    return real_decorator


def sitedata_multirun(sites):
    """
    Use as a decorator on a pytest function which uses 'rf' or 'client', to automatically request correct hostname.

    This is like the 'sitedata' decorator, but will run the test multiple times, for each SiteData label passed in as
    a list to the decorator.

    Use like the following:
    @sitedata_multirun(['catalysthunter', 'nextminingboom', 'nexttechstock'])

    If you want to get the current sitedata inside of a test:
    print(client.sitedata.label)
    """
    def real_decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            for site in sites:
                args, kwargs = _sitedata_monkeypatch(site, *args, **kwargs)
                function(*args, **kwargs)
        return wrapper
    return real_decorator


def _sitedata_monkeypatch(site, *args, **kwargs):
    """
    Core functionality of decorators above.
    This monkeypatches Client or RequestFactory with the appropriate HTTP_HOST, and adds
    a SiteData instance as an attribute (so it can be looked at inside of a test).
    """
    sitedata = SiteData(label=site, require_exact_match=True)
    if 'client' in kwargs.keys():
        kwargs['client'] = Client(HTTP_HOST=sitedata.hostname)
        kwargs['client'].sitedata = sitedata
    if 'rf' in kwargs.keys():
        kwargs['rf'] = RequestFactory(HTTP_HOST=sitedata.hostname)
        kwargs['rf'].sitedata = sitedata
    return args, kwargs
